import React, { StrictMode, Component, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class RootErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Fatal application error caught by RootErrorBoundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#050507] text-white flex flex-col items-center justify-center p-6 font-mono text-center">
          <div className="max-w-md p-6 rounded-2xl bg-[#0d0e12] border border-[#ff2a5f]/40 shadow-2xl space-y-4">
            <div className="w-12 h-12 mx-auto rounded-xl bg-[#ff2a5f]/20 text-[#ff2a5f] flex items-center justify-center text-xl font-black">
              !
            </div>
            <h1 className="text-lg font-black uppercase text-white tracking-wider">
              Сбой отображения интерфейса
            </h1>
            <p className="text-xs text-neutral-400">
              {this.state.error?.message || 'Произошла непредвиденная ошибка рендеринга.'}
            </p>
            <button
              onClick={() => {
                localStorage.clear();
                window.location.reload();
              }}
              className="px-4 py-2 rounded-xl bg-[#ccff00] text-black font-black text-xs uppercase hover:bg-[#b8e600] transition cursor-pointer"
            >
              Перезагрузить пульт управления
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RootErrorBoundary>
      <App />
    </RootErrorBoundary>
  </StrictMode>,
);
