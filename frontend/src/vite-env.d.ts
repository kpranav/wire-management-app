/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_WS_URL: string;
  readonly VITE_FEATURE_CSV_EXPORT: string;
  readonly VITE_FEATURE_ADVANCED_FILTERS: string;
  readonly VITE_FEATURE_AUDIT_LOG: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
