// TypeScript Declarations for React, JSX, and Lucide Icons
// Ensures IDE zero-error compatibility even without npm install

declare module "react" {
  export type ReactNode = any;
  export type ReactElement = any;
  export type FC<P = {}> = (props: P) => any;
  export function useState<T>(initialState: T | (() => T)): [T, (newState: T | ((prev: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useMemo<T>(factory: () => T, deps: any[] | undefined): T;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;

  export interface ChangeEvent<T = Element> {
    target: T & { value: string; [key: string]: any };
  }
  export interface MouseEvent<T = Element> {
    preventDefault: () => void;
    stopPropagation: () => void;
  }

  const React: {
    createElement: any;
    Fragment: any;
    useState: typeof useState;
    useEffect: typeof useEffect;
    useMemo: typeof useMemo;
    useCallback: typeof useCallback;
  };
  export default React;
}

declare module "react/jsx-runtime" {
  export const jsx: any;
  export const jsxs: any;
  export const Fragment: any;
}

declare namespace JSX {
  interface Element extends any {}
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare module "lucide-react" {
  import { FC } from "react";
  export interface LucideProps {
    className?: string;
    size?: number | string;
    color?: string;
    [key: string]: any;
  }
  export type LucideIcon = FC<LucideProps>;

  export const CheckCircle2: LucideIcon;
  export const AlertTriangle: LucideIcon;
  export const XCircle: LucideIcon;
  export const RefreshCw: LucideIcon;
  export const ExternalLink: LucideIcon;
  export const ShieldCheck: LucideIcon;
  export const TrendingUp: LucideIcon;
  export const BarChart3: LucideIcon;
  export const PieChart: LucideIcon;
  export const Calendar: LucideIcon;
  export const DollarSign: LucideIcon;
  export const Search: LucideIcon;
  export const Moon: LucideIcon;
  export const Sun: LucideIcon;
  export const Database: LucideIcon;
  export const ArrowUpRight: LucideIcon;
  export const Info: LucideIcon;
}
