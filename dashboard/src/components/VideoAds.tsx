// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import type { ReactNode } from 'react'
import type { PdVideoAds } from '../types'
import { NOTE } from './ui'

const LABEL: Record<string, string> = { video_horizontal: '16:9', video_vertical: '9:16', video_square: '1:1' }
const LINK = 'text-green-700 underline dark:text-green-400'

/**
 * YouTube video ads: the three cuts (16:9 in-stream, 9:16 Shorts, 1:1 in-feed), each linked to YouTube once
 * uploaded, plus the YouTube API Services links. Display only; `children` is where a host puts its buttons
 * (the Client Portal's Make / Connect / Upload).
 */
export default function VideoAds({ video, children }: { video: PdVideoAds; children?: ReactNode }) {
  const videos = Object.entries(video.videos ?? {})
  return (
    <div>
      <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Video (YouTube in-stream, in-feed, Shorts)</h3>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-sm">
        {videos.length === 0 && !children && <span className={NOTE}>No videos yet.</span>}
        {videos.map(([fmt, v]) => {
          const href = v?.youtube_id ? `https://youtu.be/${v.youtube_id}` : v?.url
          const text = `${LABEL[fmt] ?? fmt}${v?.youtube_id ? ' on YouTube' : ''}`
          return href
            ? <a key={fmt} href={href} target="_blank" rel="noreferrer" className={LINK}>{text}</a>
            : <span key={fmt} className="text-zinc-700 dark:text-zinc-300">{text}</span>
        })}
        {children}
      </div>
      <p className={`mt-1 ${NOTE}`}>
        {video.connected && video.channel_id ? <>Channel <a className="underline" href={`https://www.youtube.com/channel/${video.channel_id}`} target="_blank" rel="noreferrer">{video.channel_id}</a>{' · '}</> : null}
        Uses YouTube API Services: <a className="underline" href="https://www.youtube.com/t/terms" target="_blank" rel="noreferrer">YouTube Terms of Service</a>
        {' · '}<a className="underline" href="https://policies.google.com/privacy" target="_blank" rel="noreferrer">Google Privacy Policy</a>
        {' · '}<a className="underline" href="https://myaccount.google.com/permissions" target="_blank" rel="noreferrer">Revoke access</a>
      </p>
    </div>
  )
}
