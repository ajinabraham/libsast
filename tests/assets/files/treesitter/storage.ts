const AUTH_KEY = "user_auth_token";
const SAFE_KEY = "theme_mode";
AsyncStorage.setItem(SAFE_KEY, "dark");
AsyncStorage.setItem(AUTH_KEY, jwtValue);
