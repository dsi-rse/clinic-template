import { create } from 'zustand'

interface FiltersState {
  city: string
  setCity: (city: string) => void
  indicator: string
  setIndicator: (indicator: string) => void
}

export const useFilters = create<FiltersState>((set) => ({
  city: 'All',
  setCity: (city) => set({ city }),
  indicator: 'hardship_index',
  setIndicator: (indicator) => set({ indicator }),
}))
