import { configureStore } from '@reduxjs/toolkit'
import userReducer from './userStore'
import modalReducer from './modalStore'
import { useDispatch, useSelector } from 'react-redux'

export const store = configureStore({
    reducer: {
        user: userReducer,
        modal: modalReducer
    }
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
export type AppStore = typeof store
export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()
