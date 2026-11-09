// eval("commented out")
if (__DEV__) {
  eval("dev only");
}
eval("prod_danger");
const okStore = new MMKV({ id: "a", encryptionKey: "secret" });
const badStore = new MMKV({ id: "b" });
export const View = () => (
  <WebView
    source={{ uri: "https://example.com" }}
    allowUniversalAccessFromFileURLs={true}
  />
);
