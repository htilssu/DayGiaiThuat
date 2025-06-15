"use client";

import { useAppDispatch, useAppSelector } from '@/lib/store';
import { useDispatch } from 'react-redux';
import { ReactNode, useEffect } from 'react';
import { userApi } from '../lib/api';
import { loadingUser, setUser } from '@/lib/store/userStore'
import { authApi } from '../lib/api/auth';

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const dispatch = useAppDispatch()
  const userState = useAppSelector((state) => state.user)

  useEffect(() => {
    dispatch(loadingUser())
    userApi.getUserByToken().then((data) => {
      dispatch(setUser(data))
    });
  }, [userState.isInitial])

  return <>{children}</>;
}