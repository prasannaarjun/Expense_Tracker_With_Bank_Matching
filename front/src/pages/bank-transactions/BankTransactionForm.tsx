import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Typography,
  Paper,
  TextField,
  Alert,
} from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';

export const BankTransactionForm: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');

  const importMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await apiClient.post('/bank-transactions/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bank-transactions'] });
      navigate('/bank-transactions');
    },
    onError: (error: any) => {
      setError(error.response?.data?.message || 'Failed to import transactions');
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type === 'text/csv') {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Please select a CSV file');
        setFile(null);
      }
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    importMutation.mutate(formData);
  };

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>
        Import Bank Transactions
      </Typography>

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {error && (
              <Alert severity="error" onClose={() => setError('')}>
                {error}
              </Alert>
            )}

            <TextField
              type="file"
              inputProps={{ accept: '.csv' }}
              onChange={handleFileChange}
              error={!!error}
              helperText="Please select a CSV file containing bank transactions"
              InputLabelProps={{ shrink: true }}
            />

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                onClick={() => navigate('/bank-transactions')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={!file || importMutation.isPending}
              >
                Import
              </Button>
            </Box>
          </Box>
        </form>
      </Paper>
    </Box>
  );
}; 