/**
 * Tests for WireList component
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { WireList } from '../components/WireList';

// Mock API
vi.mock('../services/api', () => ({
  api: {
    getWires: vi.fn().mockResolvedValue({
      wires: [
        {
          id: 1,
          sender_name: 'John Doe',
          recipient_name: 'Jane Smith',
          amount: 1000.0,
          currency: 'USD',
          status: 'pending',
          reference_number: 'WIRE-ABC123',
          created_at: '2024-01-01T10:00:00Z',
          created_by: 1,
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      cached: false,
    }),
    deleteWire: vi.fn().mockResolvedValue({}),
  },
}));

// Mock WebSocket
vi.mock('../services/websocket', () => ({
  wireWebSocket: {
    connect: vi.fn(),
    disconnect: vi.fn(),
    onMessage: vi.fn(),
  },
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const renderWireList = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <WireList />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('WireList Component', () => {
  it('renders wire transfers title', () => {
    renderWireList();

    expect(screen.getByText('Wire Transfers')).toBeInTheDocument();
  });

  it('renders new wire button', () => {
    renderWireList();

    expect(screen.getByRole('button', { name: /new wire/i })).toBeInTheDocument();
  });

  it('renders table headers', async () => {
    renderWireList();

    expect(await screen.findByText('Reference')).toBeInTheDocument();
    expect(screen.getByText('Sender')).toBeInTheDocument();
    expect(screen.getByText('Recipient')).toBeInTheDocument();
    expect(screen.getByText('Amount')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
  });

  it('displays wire data', async () => {
    renderWireList();

    expect(await screen.findByText('WIRE-ABC123')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('1000.00')).toBeInTheDocument();
  });
});
