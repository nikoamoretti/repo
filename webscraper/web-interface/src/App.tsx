import { useState } from 'react'
import { FileDown, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

function App() {
  const [urls, setUrls] = useState('')
  const [filename, setFilename] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [downloadUrl, setDownloadUrl] = useState('')

  const handleSubmit = async () => {
    if (!urls.trim()) {
      setError('Please enter at least one URL')
      return
    }
    if (!filename.trim()) {
      setError('Please enter a filename')
      return
    }


    setLoading(true)
    setError('')
    try {
      const urlList = urls.split('\n').filter(url => url.trim())
      if (urlList.length === 0) {
        throw new Error('No valid URLs found')
      }

      const response = await fetch('https://user:faaea8c141c3b427ca040f3edf57c805@web-scraper-tool-tunnel-1fgpvxu9.devinapps.com/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          urls: urlList,
          filename: filename.trim()
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to process URLs')
      }

      const data = await response.json()
      setDownloadUrl(data.csvUrl)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process URLs. Please try again.')
    }
    setLoading(false)
  }

  const handleDownload = () => {
    if (downloadUrl) {
      window.location.href = `http://localhost:8000${downloadUrl}`
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto max-w-2xl px-4">
        <Card className="bg-white shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-gray-900">Web Scraper</CardTitle>
            <CardDescription>Enter URLs to scrape (one per line) and specify output filename</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">URLs</label>
              <Textarea
                placeholder="https://example.com/page1&#10;https://example.com/page2"
                value={urls}
                onChange={(e) => setUrls(e.target.value)}
                className="min-h-32"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Output Filename</label>
              <Input
                placeholder="output"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="flex justify-between items-center pt-4">
              <Button
                onClick={handleSubmit}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  'Processing...'
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Process URLs
                  </>
                )}
              </Button>

              {downloadUrl && (
                <Button variant="outline" onClick={handleDownload}>
                  <FileDown className="mr-2 h-4 w-4" />
                  Download CSV
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
