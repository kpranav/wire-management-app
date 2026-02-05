/**
 * Wire detail component for create/edit
 */
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Button,
  Container,
  Paper,
  TextField,
  Typography,
  MenuItem,
  Alert,
} from '@mui/material';
import { ArrowBack, Save } from '@mui/icons-material';
import { api } from '@/services/api';
import { WireStatus } from '@/types/wire';

const wireSchema = z.object({
  sender_name: z.string().min(1, 'Sender name is required').max(200),
  recipient_name: z.string().min(1, 'Recipient name is required').max(200),
  amount: z.number().positive('Amount must be positive'),
  currency: z.string().length(3, 'Currency must be 3 letters'),
  status: z.nativeEnum(WireStatus).optional(),
});

type WireFormData = z.infer<typeof wireSchema>;

export function WireDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEdit = !!id;

  const { data: wire } = useQuery({
    queryKey: ['wire', id],
    queryFn: () => api.getWire(Number(id)),
    enabled: isEdit,
  });

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<WireFormData>({
    resolver: zodResolver(wireSchema),
    defaultValues: {
      sender_name: '',
      recipient_name: '',
      amount: 0,
      currency: 'USD',
      status: WireStatus.PENDING,
    },
  });

  useEffect(() => {
    if (wire) {
      reset({
        sender_name: wire.sender_name,
        recipient_name: wire.recipient_name,
        amount: Number(wire.amount),
        currency: wire.currency,
        status: wire.status as WireStatus,
      });
    }
  }, [wire, reset]);

  const createMutation = useMutation({
    mutationFn: (data: WireFormData) => api.createWire(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wires'] });
      navigate('/');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: WireFormData) => api.updateWire(Number(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wires'] });
      queryClient.invalidateQueries({ queryKey: ['wire', id] });
      navigate('/');
    },
  });

  const onSubmit = async (data: WireFormData) => {
    if (isEdit) {
      await updateMutation.mutateAsync(data);
    } else {
      await createMutation.mutateAsync(data);
    }
  };

  const error = createMutation.error || updateMutation.error;

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Button startIcon={<ArrowBack />} onClick={() => navigate('/')} sx={{ mb: 2 }}>
        Back to List
      </Button>

      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {isEdit ? 'Edit Wire' : 'New Wire'}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error instanceof Error ? error.message : 'An error occurred'}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Controller
            name="sender_name"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Sender Name"
                fullWidth
                margin="normal"
                error={!!errors.sender_name}
                helperText={errors.sender_name?.message}
              />
            )}
          />

          <Controller
            name="recipient_name"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Recipient Name"
                fullWidth
                margin="normal"
                error={!!errors.recipient_name}
                helperText={errors.recipient_name?.message}
              />
            )}
          />

          <Controller
            name="amount"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                label="Amount"
                type="number"
                fullWidth
                margin="normal"
                error={!!errors.amount}
                helperText={errors.amount?.message}
                inputProps={{ step: '0.01', min: '0' }}
              />
            )}
          />

          <Controller
            name="currency"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Currency"
                fullWidth
                margin="normal"
                error={!!errors.currency}
                helperText={errors.currency?.message}
                inputProps={{ maxLength: 3 }}
              />
            )}
          />

          {isEdit && (
            <Controller
              name="status"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  select
                  label="Status"
                  fullWidth
                  margin="normal"
                  error={!!errors.status}
                  helperText={errors.status?.message}
                >
                  <MenuItem value={WireStatus.PENDING}>Pending</MenuItem>
                  <MenuItem value={WireStatus.PROCESSING}>Processing</MenuItem>
                  <MenuItem value={WireStatus.COMPLETED}>Completed</MenuItem>
                  <MenuItem value={WireStatus.FAILED}>Failed</MenuItem>
                </TextField>
              )}
            />
          )}

          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button
              type="submit"
              variant="contained"
              startIcon={<Save />}
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {isEdit ? 'Update' : 'Create'}
            </Button>
            <Button variant="outlined" onClick={() => navigate('/')}>
              Cancel
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}
