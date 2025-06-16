import React from 'react'

export default function Modal() {
    return (
        <div className='fixed z-[999999] inset-0 bg-black/50  flex justify-center items-center'>
            <div className='bg-white p-4 rounded-lg'>
                <h2 className='text-2xl font-bold'>Modal</h2>
            </div>
        </div>
    )
}