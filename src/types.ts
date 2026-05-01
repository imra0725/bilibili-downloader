export interface VideoInfo {
  bvid: string;
  title: string;
  description: string;
  cover: string;
  owner: {
    name: string;
    mid: number;
    face: string;
  };
  duration: number;
  pages: VideoPage[];
  qualities: QualityOption[];
}

export interface VideoPage {
  cid: number;
  page: number;
  part: string;
  duration: number;
}

export interface QualityOption {
  qn: number;
  desc: string;
}

export interface DownloadParams {
  url: string;
  quality: number;
  savePath: string;
  pageIndex?: number;
}

export interface DownloadRecord {
  id: string;
  bvid: string;
  title: string;
  cover: string;
  quality: string;
  save_path: string;
  filename: string;
  status: 'pending' | 'downloading' | 'completed' | 'failed';
  progress: number;
  speed: string;
  error: string;
  created_at: string;
  completed_at?: string;
}

export interface DownloadTask {
  record: DownloadRecord;
  controller?: AbortController;
}
