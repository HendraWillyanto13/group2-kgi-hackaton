import hotToast from 'react-hot-toast'

// Create a compatible toast object that matches the expected API
export const toast = {
  success: (message) => hotToast.success(message),
  error: (message) => hotToast.error(message),
  loading: (message) => hotToast.loading(message),
  dismiss: () => hotToast.dismiss(),
  promise: hotToast.promise
}