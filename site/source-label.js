// Only an explicitly recorded provider can refine the generic platform label.
export function sourceLabel(resource, platformName) {
  return resource?.platform === 'other' && resource?.source_provider === 'peertube'
    ? 'PeerTube'
    : platformName(resource?.platform);
}
