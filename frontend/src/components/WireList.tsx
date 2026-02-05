/**
 * Wire list component with grid and filters
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
} from '@mui/material';
import { Add, Edit, Delete, Refresh } from '@mui/icons-material';
import { api } from '@/services/api';
import { wireWebSocket, WireUpdateMessage } from '@/services/websocket';
import { Wire, WireStatus } from '@/types/wire';

export function WireList() {
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['wires', page + 1, pageSize, statusFilter],
    queryFn: () => api.getWires(page + 1, pageSize, statusFilter || undefined),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteWire(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wires'] });
    },
  });

  // WebSocket for real-time updates
  useEffect(() => {
    wireWebSocket.connect();

    const handleWireUpdate = (message: WireUpdateMessage | { type: string }) => {
      if (message.type === 'wire_update') {
        // Refetch wire list when an update is received
        queryClient.invalidateQueries({ queryKey: ['wires'] });
      }
    };

    wireWebSocket.onMessage(handleWireUpdate);

    return () => {
      wireWebSocket.disconnect();
    };
  }, [queryClient]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case WireStatus.COMPLETED:
        return 'success';
      case WireStatus.PROCESSING:
        return 'info';
      case WireStatus.FAILED:
        return 'error';
      default:
        return 'default';
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this wire?')) {
      await deleteMutation.mutateAsync(id);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Wire Transfers
        </Typography>
        <Box>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate('/wires/new')}
          >
            New Wire
          </Button>
        </Box>
      </Box>

      <Box sx={{ mb: 2 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Status Filter</InputLabel>
          <Select
            value={statusFilter}
            label="Status Filter"
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(0);
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value={WireStatus.PENDING}>Pending</MenuItem>
            <MenuItem value={WireStatus.PROCESSING}>Processing</MenuItem>
            <MenuItem value={WireStatus.COMPLETED}>Completed</MenuItem>
            <MenuItem value={WireStatus.FAILED}>Failed</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load wires. Please try again.
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Reference</TableCell>
              <TableCell>Sender</TableCell>
              <TableCell>Recipient</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Currency</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : data?.wires.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  No wires found
                </TableCell>
              </TableRow>
            ) : (
              data?.wires.map((wire: Wire) => (
                <TableRow key={wire.id} hover>
                  <TableCell>{wire.reference_number}</TableCell>
                  <TableCell>{wire.sender_name}</TableCell>
                  <TableCell>{wire.recipient_name}</TableCell>
                  <TableCell align="right">{Number(wire.amount).toFixed(2)}</TableCell>
                  <TableCell>{wire.currency}</TableCell>
                  <TableCell>
                    <Chip label={wire.status} color={getStatusColor(wire.status)} size="small" />
                  </TableCell>
                  <TableCell>{new Date(wire.created_at).toLocaleString()}</TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => navigate(`/wires/${wire.id}`)}
                      sx={{ mr: 1 }}
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleDelete(wire.id)} color="error">
                      <Delete fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={data?.total || 0}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={pageSize}
          onRowsPerPageChange={(e) => {
            setPageSize(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[10, 20, 50]}
        />
      </TableContainer>
    </Container>
  );
}
