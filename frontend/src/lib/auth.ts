/**
 * Insight IS — Auth Utilities
 *
 * Работает совместно с tokenStorage из apiClient.ts.
 * JWT хранится в localStorage под ключами insight_access_token / insight_refresh_token.
 * Данные профиля пользователя — под ключом insight_user.
 */

import { tokenStorage } from "./apiClient";
import type { User as ApiUser } from "./types";

export type { ApiUser as User };

// ── User profile ──────────────────────────────────────────────────────────────

const USER_KEY = "insight_user";

export const saveUser = (user: ApiUser) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const getUser = (): ApiUser | null => {
  const data = localStorage.getItem(USER_KEY);
  return data ? JSON.parse(data) : null;
};

export const removeUser = () => {
  localStorage.removeItem(USER_KEY);
};

// ── Auth state ────────────────────────────────────────────────────────────────

export const isAuthenticated = (): boolean => {
  return tokenStorage.getAccess() !== null;
};

export const logout = () => {
  tokenStorage.clear();
};
