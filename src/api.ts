import type { VideoInfo, DownloadParams, DownloadRecord } from './types';

interface PyWebviewAPI {
  parse_video(url: string): Promise<VideoInfo | { error: string }>;
  download_video(params: DownloadParams): Promise<{ task_id: string } | { error: string }>;
  select_folder(): Promise<string | null>;
  get_download_history(): Promise<DownloadRecord[]>;
  cancel_download(task_id: string): Promise<boolean>;
  open_file(path: string): Promise<boolean>;
  open_folder(path: string): Promise<boolean>;
  get_default_download_path(): Promise<string>;
}

declare global {
  interface Window {
    pywebview?: {
      api: PyWebviewAPI;
    };
  }
}

const hasPyWebview = (): boolean => {
  return typeof window !== 'undefined' && !!window.pywebview?.api;
};

const callApi = async <T,>(
  method: keyof PyWebviewAPI,
  ...args: unknown[]
): Promise<T> => {
  if (!hasPyWebview()) {
    throw new Error('PyWebview API not available');
  }
  const fn = window.pywebview!.api[method] as (...args: unknown[]) => Promise<T>;
  return fn(...args);
};

export const api = {
  isAvailable: hasPyWebview,

  parseVideo: (url: string) => callApi<VideoInfo | { error: string }>('parse_video', url),

  downloadVideo: (params: DownloadParams) => callApi<{ task_id: string } | { error: string }>('download_video', params),

  selectFolder: () => callApi<string | null>('select_folder'),

  getDownloadHistory: () => callApi<DownloadRecord[]>('get_download_history'),

  cancelDownload: (taskId: string) => callApi<boolean>('cancel_download', taskId),

  openFile: (path: string) => callApi<boolean>('open_file', path),

  openFolder: (path: string) => callApi<boolean>('open_folder', path),

  getDefaultDownloadPath: () => callApi<string>('get_default_download_path'),
};
