import { useState, useEffect, useCallback } from 'react'
import {
  Download, History, Search, FolderOpen, Play, X, CheckCircle,
  AlertCircle, Loader2, FileVideo, Sparkles, ExternalLink, Folder
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { VideoInfo, DownloadRecord } from './types'
import { api } from './api'

const TAB_DOWNLOAD = 'download'
const TAB_HISTORY = 'history'

export default function App() {
  const [activeTab, setActiveTab] = useState(TAB_DOWNLOAD)
  const [url, setUrl] = useState('')
  const [parsing, setParsing] = useState(false)
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null)
  const [parseError, setParseError] = useState('')
  const [selectedQuality, setSelectedQuality] = useState('80')
  const [selectedPage, setSelectedPage] = useState(0)
  const [savePath, setSavePath] = useState('')
  const [history, setHistory] = useState<DownloadRecord[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)

  const isPyWebviewReady = api.isAvailable()

  const activeDownloads = history.filter(r => r.status === 'downloading' || r.status === 'pending')
  const hasActiveDownloads = activeDownloads.length > 0

  // Initialize and polling
  useEffect(() => {
    if (isPyWebviewReady) {
      api.getDefaultDownloadPath().then((path: string) => setSavePath(path)).catch(() => setSavePath(''))
      loadHistory()
    }
  }, [isPyWebviewReady])

  // Polling for active downloads
  useEffect(() => {
    if (!hasActiveDownloads) return
    const interval = setInterval(() => {
      loadHistory()
    }, 1000)
    return () => clearInterval(interval)
  }, [hasActiveDownloads, isPyWebviewReady])

  const loadHistory = useCallback(async () => {
    if (!isPyWebviewReady) return
    setLoadingHistory(true)
    try {
      const records = await api.getDownloadHistory()
      setHistory(records)
    } catch (e) {
      console.error('Failed to load history', e)
    } finally {
      setLoadingHistory(false)
    }
  }, [isPyWebviewReady])

  const handleParse = async () => {
    if (!url.trim()) return
    setParsing(true)
    setParseError('')
    setVideoInfo(null)
    try {
      const result = await api.parseVideo(url.trim())
      if ('error' in result) {
        setParseError(result.error)
      } else {
        setVideoInfo(result)
        if (result.qualities.length > 0) {
          setSelectedQuality(String(result.qualities[0].qn))
        }
        setSelectedPage(0)
      }
    } catch (e: any) {
      setParseError(e.message || '解析失败')
    } finally {
      setParsing(false)
    }
  }

  const handleSelectFolder = async () => {
    if (!isPyWebviewReady) return
    try {
      const path = await api.selectFolder()
      if (path) setSavePath(path)
    } catch (e) {
      console.error(e)
    }
  }

  const handleDownload = async () => {
    if (!videoInfo || !savePath) return
    try {
      const result = await api.downloadVideo({
        url: url.trim(),
        quality: parseInt(selectedQuality),
        savePath,
        pageIndex: selectedPage,
      })
      if ('error' in result) {
        alert(result.error)
      } else {
        loadHistory()
      }
    } catch (e: any) {
      alert(e.message || '下载失败')
    }
  }

  const handleCancel = async (taskId: string) => {
    try {
      await api.cancelDownload(taskId)
      loadHistory()
    } catch (e) {
      console.error(e)
    }
  }

  const handleOpenFile = async (path: string) => {
    if (!isPyWebviewReady) return
    try {
      await api.openFile(path)
    } catch (e) {
      console.error(e)
    }
  }

  const handleOpenFolder = async (path: string) => {
    if (!isPyWebviewReady) return
    try {
      await api.openFolder(path)
    } catch (e) {
      console.error(e)
    }
  }

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr)
      return d.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    } catch {
      return dateStr
    }
  }

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0a] text-white overflow-hidden select-none">
      {/* Title Bar */}
      <header className="h-12 flex items-center px-4 border-b border-white/5 shrink-0" style={{ appRegion: 'drag' } as any}>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-[#FB7299] flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <h1 className="text-sm font-semibold tracking-tight text-white/90">B站视频下载器</h1>
        </div>
        <div className="ml-auto flex items-center gap-1">
          <Badge variant="secondary" className="text-[10px] h-5 bg-white/5 text-white/40 border-0 font-normal">
            v1.0.0
          </Badge>
        </div>
      </header>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
        <div className="px-4 pt-3 pb-1 shrink-0">
          <TabsList className="w-full h-9 bg-white/5 p-1 rounded-lg border border-white/5">
            <TabsTrigger
              value={TAB_DOWNLOAD}
              className="flex-1 h-7 text-xs rounded-md data-[state=active]:bg-[#FB7299]/15 data-[state=active]:text-[#FB7299] data-[state=active]:shadow-none text-white/50 transition-all"
            >
              <Download className="w-3.5 h-3.5 mr-1.5" />
              下载视频
            </TabsTrigger>
            <TabsTrigger
              value={TAB_HISTORY}
              className="flex-1 h-7 text-xs rounded-md data-[state=active]:bg-[#FB7299]/15 data-[state=active]:text-[#FB7299] data-[state=active]:shadow-none text-white/50 transition-all"
            >
              <History className="w-3.5 h-3.5 mr-1.5" />
              下载记录
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value={TAB_DOWNLOAD} className="flex-1 flex flex-col overflow-hidden m-0 px-4 pb-4 mt-2">
          <ScrollArea className="flex-1 pr-2">
            <div className="space-y-4">
              {/* URL Input Section */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-white/50 ml-1">视频链接</label>
                <div className="flex gap-2">
                  <Input
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="粘贴B站视频链接，如 https://www.bilibili.com/video/BV1xx411c7mD"
                    className="flex-1 h-10 bg-white/5 border-white/10 text-sm text-white placeholder:text-white/20 focus-visible:ring-[#FB7299]/50 focus-visible:ring-1 focus-visible:border-[#FB7299]/30 rounded-xl"
                    onKeyDown={(e) => e.key === 'Enter' && handleParse()}
                  />
                  <Button
                    onClick={handleParse}
                    disabled={parsing || !url.trim()}
                    className="h-10 px-4 bg-[#FB7299] hover:bg-[#FB7299]/90 text-white rounded-xl text-sm font-medium shrink-0 disabled:opacity-50"
                  >
                    {parsing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                    <span className="ml-1.5">{parsing ? '解析中' : '解析'}</span>
                  </Button>
                </div>
              </div>

              {/* Error Message */}
              {parseError && (
                <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  {parseError}
                </div>
              )}

              {/* Video Info Card */}
              {videoInfo && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 space-y-4">
                    {/* Cover & Title */}
                    <div className="flex gap-3">
                      <div className="w-32 h-20 rounded-xl bg-white/5 overflow-hidden shrink-0 relative">
                        {videoInfo.cover ? (
                          <img src={videoInfo.cover} alt="cover" className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <FileVideo className="w-6 h-6 text-white/20" />
                          </div>
                        )}
                        <div className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/60 text-[10px] text-white/90 font-medium">
                          {formatDuration(videoInfo.duration)}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-semibold text-white/90 leading-snug line-clamp-2">{videoInfo.title}</h3>
                        <div className="flex items-center gap-1.5 mt-1.5">
                          <div className="w-4 h-4 rounded-full bg-white/10 overflow-hidden">
                            {videoInfo.owner.face && (
                              <img src={videoInfo.owner.face} alt="avatar" className="w-full h-full object-cover" />
                            )}
                          </div>
                          <span className="text-xs text-white/50">{videoInfo.owner.name}</span>
                        </div>
                        <p className="text-[11px] text-white/30 mt-1 line-clamp-1">{videoInfo.bvid}</p>
                      </div>
                    </div>

                    {/* Page Selection */}
                    {videoInfo.pages.length > 1 && (
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-white/50 ml-1">选择分P</label>
                        <Select value={String(selectedPage)} onValueChange={(v) => setSelectedPage(Number(v))}>
                          <SelectTrigger className="h-9 bg-white/5 border-white/10 text-xs text-white rounded-xl focus:ring-[#FB7299]/50">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-[#141414] border-white/10 text-white rounded-xl">
                            {videoInfo.pages.map((page, idx) => (
                              <SelectItem key={page.cid} value={String(idx)} className="text-xs focus:bg-[#FB7299]/10 focus:text-white">
                                P{page.page} {page.part} ({formatDuration(page.duration)})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    {/* Quality Selection */}
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-white/50 ml-1">清晰度</label>
                      <Select value={selectedQuality} onValueChange={setSelectedQuality}>
                        <SelectTrigger className="h-9 bg-white/5 border-white/10 text-xs text-white rounded-xl focus:ring-[#FB7299]/50">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-[#141414] border-white/10 text-white rounded-xl">
                          {videoInfo.qualities.map((q) => (
                            <SelectItem key={q.qn} value={String(q.qn)} className="text-xs focus:bg-[#FB7299]/10 focus:text-white">
                              {q.desc}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Save Path */}
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-white/50 ml-1">保存路径</label>
                      <div className="flex gap-2">
                        <Input
                          value={savePath}
                          readOnly
                          placeholder="点击右侧按钮选择下载文件夹"
                          className="flex-1 h-9 bg-white/5 border-white/10 text-xs text-white placeholder:text-white/20 rounded-xl"
                        />
                        <Button
                          variant="outline"
                          onClick={handleSelectFolder}
                          className="h-9 px-3 border-white/10 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white rounded-xl text-xs shrink-0"
                        >
                          <FolderOpen className="w-3.5 h-3.5 mr-1" />
                          浏览
                        </Button>
                      </div>
                    </div>

                    {/* Download Button */}
                    <Button
                      onClick={handleDownload}
                      disabled={!savePath}
                      className="w-full h-10 bg-[#FB7299] hover:bg-[#FB7299]/90 text-white rounded-xl text-sm font-semibold disabled:opacity-40 transition-all"
                    >
                      <Download className="w-4 h-4 mr-1.5" />
                      开始下载
                    </Button>
                  </div>
                </div>
              )}

              {/* Active Downloads */}
              {activeDownloads.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wider ml-1">当前下载</h3>
                  {activeDownloads.map((record) => (
                    <div key={record.id} className="p-3 rounded-xl bg-white/[0.03] border border-white/5 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-white/80 truncate pr-2">{record.title}</span>
                        <div className="flex items-center gap-1 shrink-0">
                          {record.status === 'downloading' && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleCancel(record.id)}
                              className="w-6 h-6 hover:bg-white/10 text-white/50"
                            >
                              <X className="w-3 h-3" />
                            </Button>
                          )}
                          {record.status === 'completed' && (
                            <CheckCircle className="w-4 h-4 text-emerald-400" />
                          )}
                          {record.status === 'failed' && (
                            <AlertCircle className="w-4 h-4 text-red-400" />
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress value={record.progress} className="h-1.5 flex-1 bg-white/5" />
                        <span className="text-[10px] text-white/40 w-10 text-right">{record.progress}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-white/30">{record.speed || '准备中...'}</span>
                        <span className="text-[10px] text-white/30">{record.quality}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value={TAB_HISTORY} className="flex-1 flex flex-col overflow-hidden m-0 px-4 pb-4 mt-2">
          <ScrollArea className="flex-1 pr-2">
            <div className="space-y-3">
              {loadingHistory ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-5 h-5 animate-spin text-[#FB7299]" />
                </div>
              ) : history.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-white/20">
                  <History className="w-8 h-8 mb-3" />
                  <p className="text-xs">暂无下载记录</p>
                </div>
              ) : (
                history.map((record) => (
                  <div
                    key={record.id}
                    className="group p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-[#FB7299]/20 hover:bg-white/[0.05] transition-all"
                  >
                    <div className="flex gap-3">
                      <div className="w-16 h-10 rounded-lg bg-white/5 overflow-hidden shrink-0 relative">
                        {record.cover ? (
                          <img src={record.cover} alt="cover" className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <FileVideo className="w-4 h-4 text-white/20" />
                          </div>
                        )}
                        <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Play className="w-4 h-4 text-white" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-xs font-medium text-white/80 truncate">{record.title}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="secondary" className="text-[10px] h-4 px-1 bg-white/5 text-white/40 border-0">
                            {record.quality}
                          </Badge>
                          <span className="text-[10px] text-white/30">{formatDate(record.created_at)}</span>
                        </div>
                        {record.status === 'failed' && record.error && (
                          <p className="text-[10px] text-red-400/70 mt-1 line-clamp-1">{record.error}</p>
                        )}
                      </div>
                      <div className="flex flex-col items-end gap-1 shrink-0">
                        {record.status === 'completed' ? (
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleOpenFile(record.save_path + '\\' + record.filename)}
                              className="w-7 h-7 hover:bg-white/10 text-white/40 hover:text-white"
                            >
                              <ExternalLink className="w-3.5 h-3.5" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleOpenFolder(record.save_path)}
                              className="w-7 h-7 hover:bg-white/10 text-white/40 hover:text-white"
                            >
                              <Folder className="w-3.5 h-3.5" />
                            </Button>
                          </div>
                        ) : record.status === 'failed' ? (
                          <Badge variant="destructive" className="text-[10px] h-5 bg-red-500/10 text-red-400 border-red-500/20">
                            失败
                          </Badge>
                        ) : (
                          <Badge className="text-[10px] h-5 bg-[#FB7299]/10 text-[#FB7299] border-[#FB7299]/20">
                            下载中
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  )
}
