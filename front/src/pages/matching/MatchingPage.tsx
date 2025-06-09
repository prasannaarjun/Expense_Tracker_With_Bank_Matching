import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Stack,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  CompareArrows as CompareIcon,
  Check as CheckIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { format } from 'date-fns';

interface BankTransaction {
  id: number;
  date: string;
  amount: number;
  description: string;
  bank_name: string;
  account_number: string;
  is_matched: boolean;
  transaction_id?: number;
}

interface Transaction {
  id: number;
  date: string;
  amount: number;
  description: string;
  category: string;
  matched: boolean;
  bank_transaction_id?: number;
}

interface MatchDialogProps {
  open: boolean;
  onClose: () => void;
  bankTransaction: BankTransaction;
  transaction: Transaction;
  onMatch: () => void;
}

const MatchDialog: React.FC<MatchDialogProps> = ({
  open,
  onClose,
  bankTransaction,
  transaction,
  onMatch,
}) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Confirm Match</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 2 }}>
          <Typography variant="h6">Bank Transaction</Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>{format(new Date(bankTransaction.date), 'MMM dd, yyyy')}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Amount</TableCell>
                  <TableCell>${bankTransaction.amount.toFixed(2)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Description</TableCell>
                  <TableCell>{bankTransaction.description}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Bank</TableCell>
                  <TableCell>{bankTransaction.bank_name}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>

          <Typography variant="h6">Regular Transaction</Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>{format(new Date(transaction.date), 'MMM dd, yyyy')}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Amount</TableCell>
                  <TableCell>${transaction.amount.toFixed(2)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Description</TableCell>
                  <TableCell>{transaction.description}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Category</TableCell>
                  <TableCell>{transaction.category}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} startIcon={<CloseIcon />}>
          Cancel
        </Button>
        <Button onClick={onMatch} variant="contained" startIcon={<CheckIcon />}>
          Confirm Match
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const MatchingPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedBankTx, setSelectedBankTx] = useState<BankTransaction | null>(null);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);
  const [matchDialogOpen, setMatchDialogOpen] = useState(false);

  useEffect(() => {
    if (selectedBankTx && selectedTx) {
      setMatchDialogOpen(true);
    }
  }, [selectedBankTx, selectedTx]);

  const { data: bankTransactions, isLoading: isLoadingBank } = useQuery({
    queryKey: ['unmatchedBankTransactions'],
    queryFn: async () => {
      const response = await apiClient.get<BankTransaction[]>('/bank-transactions/', {
        params: { is_matched: false },
      });
      return response.data;
    },
  });

  const { data: transactions, isLoading: isLoadingTransactions } = useQuery({
    queryKey: ['unmatchedTransactions'],
    queryFn: async () => {
      const response = await apiClient.get<Transaction[]>('/transactions/', {
        params: { matched: false },
      });
      return response.data;
    },
  });

  const matchMutation = useMutation({
    mutationFn: async ({ bankTxId, txId }: { bankTxId: number; txId: number }) => {
      await apiClient.post(`/bank-transactions/${bankTxId}/match`, { transaction_id: txId });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['unmatchedBankTransactions'] });
      queryClient.invalidateQueries({ queryKey: ['unmatchedTransactions'] });
      setMatchDialogOpen(false);
      setSelectedBankTx(null);
      setSelectedTx(null);
    },
  });

  const handleConfirmMatch = () => {
    if (selectedBankTx && selectedTx) {
      matchMutation.mutate({
        bankTxId: selectedBankTx.id,
        txId: selectedTx.id,
      });
    }
  };

  if (isLoadingBank || isLoadingTransactions) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>
        Match Transactions
      </Typography>

      <Stack direction="row" spacing={3}>
        {/* Bank Transactions */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Unmatched Bank Transactions
          </Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Bank</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {bankTransactions?.map((tx) => (
                  <TableRow
                    key={tx.id}
                    sx={{
                      backgroundColor: selectedBankTx?.id === tx.id ? 'action.selected' : 'inherit',
                      cursor: 'pointer',
                    }}
                  >
                    <TableCell>{format(new Date(tx.date), 'MMM dd, yyyy')}</TableCell>
                    <TableCell>${tx.amount.toFixed(2)}</TableCell>
                    <TableCell>{tx.description}</TableCell>
                    <TableCell>{tx.bank_name}</TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        color={selectedBankTx?.id === tx.id ? 'secondary' : 'primary'}
                        onClick={() => setSelectedBankTx(selectedBankTx?.id === tx.id ? null : tx)}
                      >
                        <CompareIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>

        {/* Regular Transactions */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Unmatched Regular Transactions
          </Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {transactions?.map((tx) => (
                  <TableRow
                    key={tx.id}
                    sx={{
                      backgroundColor: selectedTx?.id === tx.id ? 'action.selected' : 'inherit',
                      cursor: 'pointer',
                    }}
                  >
                    <TableCell>{format(new Date(tx.date), 'MMM dd, yyyy')}</TableCell>
                    <TableCell>${tx.amount.toFixed(2)}</TableCell>
                    <TableCell>{tx.description}</TableCell>
                    <TableCell>{tx.category}</TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        color={selectedTx?.id === tx.id ? 'secondary' : 'primary'}
                        onClick={() => setSelectedTx(selectedTx?.id === tx.id ? null : tx)}
                      >
                        <CompareIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Stack>

      {/* Match Dialog */}
      {selectedBankTx && selectedTx && (
        <MatchDialog
          open={matchDialogOpen}
          onClose={() => {
            setMatchDialogOpen(false);
            setSelectedBankTx(null);
            setSelectedTx(null);
          }}
          bankTransaction={selectedBankTx}
          transaction={selectedTx}
          onMatch={handleConfirmMatch}
        />
      )}
    </Box>
  );
};

export default MatchingPage; 