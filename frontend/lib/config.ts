const fallbackApiBaseUrl = "http://127.0.0.1:8000/api/v1";


function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, "");
}


export const appConfig = {
  appName: process.env.NEXT_PUBLIC_APP_NAME?.trim() || "Reading ELLA",
  apiBaseUrl: trimTrailingSlash(process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || fallbackApiBaseUrl),
} as const;
