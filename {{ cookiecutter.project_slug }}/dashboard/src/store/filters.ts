import { create } from 'zustand'

interface FiltersState {
  city: string
  setCity: (city: string) => void
}

export const useFilters = create<FiltersState>((set) => ({
  city: 'All',
  setCity: (city) => set({ city }),
}))
