export function formatDate(date: string | Date, options?: Intl.DateTimeFormatOptions): string {
  return new Date(date).toLocaleDateString('en-GB', options || {
    weekday: 'short', day: 'numeric', month: 'short', year: 'numeric',
  })
}

export function formatRelative(date: string | Date): string {
  const diff = Date.now() - new Date(date).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7)  return `${days} days ago`
  if (days < 30) return `${Math.floor(days / 7)} week${days >= 14 ? 's' : ''} ago`
  return formatDate(date)
}

export function formatTime(date: string | Date): string {
  return new Date(date).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function truncate(str: string, max = 80): string {
  return str.length <= max ? str : str.slice(0, max - 3) + '...'
}
