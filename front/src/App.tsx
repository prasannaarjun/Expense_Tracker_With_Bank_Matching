import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useAuth } from './contexts/AuthContext';
import { theme } from './styles/theme';
import { AuthProvider } from '@/contexts/AuthContext';
import { Layout } from '@/components/Layout';
import { LoginPage } from './pages/auth/Login';
import { RegisterPage } from './pages/auth/Register';
import { TransactionList } from './pages/transactions/TransactionList';
import { TransactionForm } from './pages/transactions/TransactionForm';
import BankTransactionList from './pages/bank-transactions/BankTransactionList';
import { BankTransactionForm } from './pages/bank-transactions/BankTransactionForm';
import MatchingPage from './pages/matching/MatchingPage';

const queryClient = new QueryClient();

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route
                path="/"
                element={
                  <PrivateRoute>
                    <Layout>
                      <TransactionList />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/transactions"
                element={
                  <PrivateRoute>
                    <Layout>
                      <TransactionList />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/transactions/new"
                element={
                  <PrivateRoute>
                    <Layout>
                      <TransactionForm />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/transactions/:id/edit"
                element={
                  <PrivateRoute>
                    <Layout>
                      <TransactionForm />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/bank-transactions"
                element={
                  <PrivateRoute>
                    <Layout>
                      <BankTransactionList />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/bank-transactions/new"
                element={
                  <PrivateRoute>
                    <Layout>
                      <BankTransactionForm />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/bank-transactions/:id/edit"
                element={
                  <PrivateRoute>
                    <Layout>
                      <BankTransactionForm />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/matching"
                element={
                  <PrivateRoute>
                    <Layout>
                      <MatchingPage />
                    </Layout>
                  </PrivateRoute>
                }
              />
            </Routes>
          </AuthProvider>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App; 