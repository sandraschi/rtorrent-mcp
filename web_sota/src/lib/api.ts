/// <reference types="vite/client" />

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, "") ??
  "http://127.0.0.1:10910";

export { API_BASE };
export default API_BASE;
