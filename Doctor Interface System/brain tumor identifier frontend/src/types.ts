export interface PredictionResult {
  type: keyof Probabilities
  probabilities: Probabilities
}

export interface Probabilities {
  glioma: number
  meningioma: number
  notumor: number
  pituitary: number
}
