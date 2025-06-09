import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  
  MenuItem,
  Stack,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { format } from 'date-fns';

type FilterType = 'date' | 'month' | 'week' | 'year';

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

const BankTransactionList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [filterType, setFilterType] = useState<FilterType | ''>('');
  const [filterValue, setFilterValue] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<string>('');
  const [selectedMonth, setSelectedMonth] = useState<string>('');
  const [selectedWeek, setSelectedWeek] = useState<string>('');

  const { data: transactions, isLoading } = useQuery({
    queryKey: ['bankTransactions', filterType, filterValue],
    queryFn: async () => {
      const response = await apiClient.get<BankTransaction[]>('/bank-transactions/', {
        params: {
          filter_type: filterType,
          filter_value: filterValue,
        },
      });
      return response.data;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/bank-transactions/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bankTransactions'] });
    },
  });

  const handleFilterChange = () => {
    if (!filterType) {
      setFilterValue('');
      setSelectedYear('');
      setSelectedMonth('');
      setSelectedWeek('');
      return;
    }

    if (filterType === 'month') {
      if (selectedYear && selectedMonth) {
        setFilterValue(`${selectedYear}-${selectedMonth}`);
      } else {
        setFilterValue('');
      }
    } else if (filterType === 'week') {
      if (selectedYear && selectedWeek) {
        setFilterValue(`${selectedYear}-${selectedWeek}`);
      } else {
        setFilterValue('');
      }
    }

    queryClient.invalidateQueries({ queryKey: ['bankTransactions'] });
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this transaction?')) {
      deleteMutation.mutate(id);
    }
  };

  const getStatusColor = (isMatched: boolean) => {
    return isMatched ? 'success' : 'warning';
  };

  // Helper functions to generate filter options
  const generateDateOptions = () => {
    const dates = [];
    const today = new Date();
    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      dates.push(date.toISOString().split('T')[0]);
    }
    return dates;
  };

  const generateMonthOptions = () => [
    { value: '01', label: 'January' },
    { value: '02', label: 'February' },
    { value: '03', label: 'March' },
    { value: '04', label: 'April' },
    { value: '05', label: 'May' },
    { value: '06', label: 'June' },
    { value: '07', label: 'July' },
    { value: '08', label: 'August' },
    { value: '09', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' }
  ];

  const generateWeekNumberOptions = () => {
    return Array.from({ length: 52 }, (_, i) => {
      const weekNum = i + 1;
      return {
        value: weekNum.toString().padStart(2, '0'),
        label: `Week ${weekNum}`
      };
    });
  };

  const generateYearOptions = () => {
    const years = [];
    const currentYear = new Date().getFullYear();
    for (let i = 0; i < 10; i++) {
      years.push((currentYear - i).toString());
    }
    return years;
  };

  const handleDownloadUnmatched = async () => {
    try {
      const response = await apiClient.get('/bank-transactions/unmatched/report', {
        responseType: 'blob', // Important for downloading files
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'unmatched_transactions.xlsx'); // or any other filename you want
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      console.error('Error downloading unmatched transactions:', error);
      // Optionally, show an error message to the user
    }
  };

  if (isLoading) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5">Bank Transactions</Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/bank-transactions/new')}
          >
            Add Transaction
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleDownloadUnmatched}
          >
            Download Unmatched
          </Button>
        </Stack>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Filter Type</InputLabel>
            <Select
              value={filterType}
              label="Filter Type"
              onChange={(e) => {
                setFilterType(e.target.value as FilterType | '');
                setFilterValue('');
                setSelectedYear('');
                setSelectedMonth('');
                setSelectedWeek('');
              }}
            >
              <MenuItem value="">No Filter</MenuItem>
              <MenuItem value="date">Date</MenuItem>
              <MenuItem value="month">Month</MenuItem>
              <MenuItem value="week">Week</MenuItem>
              <MenuItem value="year">Year</MenuItem>
            </Select>
          </FormControl>

          {filterType && (
            <>
              {filterType === 'month' ? (
                <>
                  <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel>Year</InputLabel>
                    <Select
                      value={selectedYear}
                      label="Year"
                      onChange={(e) => setSelectedYear(e.target.value)}
                    >
                      <MenuItem value="">Select Year</MenuItem>
                      {generateYearOptions().map((year) => (
                        <MenuItem key={year} value={year}>
                          {year}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel>Month</InputLabel>
                    <Select
                      value={selectedMonth}
                      label="Month"
                      onChange={(e) => setSelectedMonth(e.target.value)}
                    >
                      <MenuItem value="">Select Month</MenuItem>
                      {generateMonthOptions().map((month) => (
                        <MenuItem key={month.value} value={month.value}>
                          {month.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </>
              ) : filterType === 'week' ? (
                <>
                  <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel>Year</InputLabel>
                    <Select
                      value={selectedYear}
                      label="Year"
                      onChange={(e) => setSelectedYear(e.target.value)}
                    >
                      <MenuItem value="">Select Year</MenuItem>
                      {generateYearOptions().map((year) => (
                        <MenuItem key={year} value={year}>
                          {year}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl sx={{ minWidth: 120 }}>
                    <InputLabel>Week</InputLabel>
                    <Select
                      value={selectedWeek}
                      label="Week"
                      onChange={(e) => setSelectedWeek(e.target.value)}
                    >
                      <MenuItem value="">Select Week</MenuItem>
                      {generateWeekNumberOptions().map((week) => (
                        <MenuItem key={week.value} value={week.value}>
                          {week.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </>
              ) : (
                <FormControl sx={{ minWidth: 120 }}>
                  <InputLabel>{filterType}</InputLabel>
                  <Select
                    value={filterValue}
                    label={filterType}
                    onChange={(e) => setFilterValue(e.target.value)}
                  >
                    <MenuItem value="">Select {filterType}</MenuItem>
                    {filterType === 'date' && generateDateOptions().map((date) => (
                      <MenuItem key={date} value={date}>
                        {new Date(date).toLocaleDateString()}
                      </MenuItem>
                    ))}
                    {filterType === 'year' && generateYearOptions().map((year) => (
                      <MenuItem key={year} value={year}>
                        {year}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
              <Button
                variant="contained"
                onClick={handleFilterChange}
                disabled={
                  filterType === 'month' 
                    ? !(selectedYear && selectedMonth)
                    : filterType === 'week'
                    ? !(selectedYear && selectedWeek)
                    : !filterValue
                }
              >
                Apply Filter
              </Button>
            </>
          )}
        </Stack>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Bank Name</TableCell>
              <TableCell>Account Number</TableCell>
              <TableCell>Matched Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transactions?.map((transaction) => (
              <TableRow key={transaction.id}>
                <TableCell>{format(new Date(transaction.date), 'MMM dd, yyyy')}</TableCell>
                <TableCell>${transaction.amount.toFixed(2)}</TableCell>
                <TableCell>{transaction.description}</TableCell>
                <TableCell>{transaction.bank_name}</TableCell>
                <TableCell>{transaction.account_number}</TableCell>
                <TableCell>
                  <Chip
                    label={transaction.is_matched ? 'Matched' : 'Unmatched'}
                    color={getStatusColor(transaction.is_matched)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => navigate(`/bank-transactions/${transaction.id}/edit`)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(transaction.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default BankTransactionList; 