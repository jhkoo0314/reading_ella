const KST_OFFSET_MS = 9 * 60 * 60 * 1000;


export function getCurrentKstIsoTimestamp() {
  return new Date(Date.now() + KST_OFFSET_MS).toISOString().replace("Z", "+09:00");
}
