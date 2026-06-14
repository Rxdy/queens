import { vi } from 'vitest'

// URL.createObjectURL / revokeObjectURL ne sont pas dispo en jsdom
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
global.URL.revokeObjectURL = vi.fn()

// navigator.clipboard non dispo en jsdom
Object.defineProperty(navigator, 'clipboard', {
  value: { writeText: vi.fn().mockResolvedValue(undefined) },
  writable: true,
})

// HTMLCanvasElement.getContext (downloadGridAsImage)
HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
  fillStyle: '',
  strokeStyle: '',
  lineWidth: 0,
  fillRect: vi.fn(),
  strokeRect: vi.fn(),
}))
HTMLCanvasElement.prototype.toBlob = vi.fn((cb) => cb(new Blob()))
