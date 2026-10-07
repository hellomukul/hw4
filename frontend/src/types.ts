/** Shapes returned by the Campus Customs API (backend/main.py). */

export interface SizeStock {
  size: string
  quantity: number
}

export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  /** Already decoded by the backend — the DB stores these as JSON strings. */
  colors: string[]
  search_tags: string[]
  image_file_path: string
  image_url: string
  price: number
  total_stock?: number
  sizes_in_stock?: string[]
  /** Only on the single-product endpoint. */
  inventory?: SizeStock[]
}

export interface ProductList {
  count: number
  products: Product[]
}

export interface GarmentType {
  value: string
  label: string
  count: number
}

export interface Filters {
  garment_types: GarmentType[]
  colors: { value: string; count: number }[]
  price: { min: number; max: number }
  sizes: string[]
}
