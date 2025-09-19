# Frontend - Image Upload Application

A modern React application built with Vite, Tailwind CSS, and shadcn/ui for uploading images to a FastAPI backend.

## Features

- 🖼️ **Multi-file Image Upload**: Select and upload multiple image files simultaneously
- 📊 **Real-time Progress**: Visual progress bar with percentage feedback during uploads
- 🎨 **Modern UI**: Clean, accessible interface built with Tailwind CSS and shadcn/ui components
- ♿ **Accessibility First**: Full keyboard navigation, ARIA labels, and screen reader support
- 📱 **Responsive Design**: Works seamlessly across desktop and mobile devices
- 🔥 **Hot Reload**: Instant development feedback with Vite
- 🚨 **Error Handling**: User-friendly error messages and upload retry functionality

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite 7.x
- **Styling**: Tailwind CSS 3.4+
- **UI Components**: shadcn/ui
- **HTTP Client**: Axios
- **Routing**: React Router DOM
- **Toast Notifications**: React Hot Toast

## Prerequisites

- Node.js 16+ or higher
- npm or yarn package manager
- Backend server running on port 8000 (see backend README)

## Environment Setup

### Environment Variables

Create a `.env` file in the frontend directory:

```env
# Backend API URL - required for API communication
VITE_API_BASE_URL=http://localhost:8000
```

**Important**: The `VITE_API_BASE_URL` variable is required for the frontend to communicate with the backend API.

## Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   ```bash
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   ```

## Running the Application

### Development Server (Recommended)

Start the development server with hot reload:

```bash
npm run dev
```

The application will be available at `http://localhost:5173/`

### Build for Production

Create an optimized production build:

```bash
npm run build
```

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## Available Routes

- **Home** (`/`) - Main application with component demos
- **Upload** (`/upload`) - Image upload interface

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/
│   │   └── ui/            # shadcn/ui components
│   │       ├── button.jsx
│   │       ├── input.jsx
│   │       ├── progress.jsx
│   │       └── toaster.jsx
│   ├── hooks/
│   │   └── use-toast.js   # Toast notification hook
│   ├── lib/
│   │   ├── api.js         # API client functions
│   │   └── utils.js       # Utility functions
│   ├── pages/
│   │   └── UploadPage.jsx # Main upload interface
│   ├── assets/            # Application assets
│   ├── App.jsx           # Root component
│   ├── main.jsx          # Application entry point
│   └── index.css         # Global styles
├── .env                   # Environment variables
├── package.json          # Dependencies and scripts
├── vite.config.js        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── README.md             # This file
```

## API Integration

The frontend communicates with the FastAPI backend via the `/api/upload` endpoint:

- **Endpoint**: `POST {VITE_API_BASE_URL}/api/upload`
- **Content-Type**: `multipart/form-data`
- **Body**: Files are sent with the field name `files` (multiple files supported)
- **Response**: JSON with upload results and file information

## Upload Workflow

1. **File Selection**: Users click "Select Images" to choose image files
2. **File Validation**: Only image files are accepted (JPEG, PNG, GIF, WebP, etc.)
3. **Upload Process**: Click "Upload Images" to start the upload
4. **Progress Tracking**: Real-time progress bar shows upload percentage
5. **Completion**: Success/error notifications with automatic UI reset

## Accessibility Features

- ✅ **Keyboard Navigation**: All interactive elements are keyboard accessible
- ✅ **Focus Management**: Visible focus indicators on all buttons and inputs
- ✅ **Screen Reader Support**: Proper ARIA labels and descriptions
- ✅ **Live Regions**: Upload progress announced to screen readers
- ✅ **Semantic HTML**: Proper heading structure and form elements

## Development

### Adding New Components

The project uses shadcn/ui for consistent component styling. To add new components:

```bash
# Example: Adding a new Card component
npx shadcn-ui@latest add card
```

### Customizing Styles

- **Global Styles**: Edit `src/index.css`
- **Tailwind Config**: Modify `tailwind.config.js`
- **Component Styles**: Use Tailwind classes directly in JSX

## Testing the Upload Feature

### Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend server running on `http://localhost:5173`
3. Environment variable `VITE_API_BASE_URL` properly set

### Test Steps
1. Navigate to `http://localhost:5173/upload`
2. Click "Select Images" and choose image files
3. Verify files appear in the list with correct names and sizes
4. Click "Upload Images" and watch the progress bar
5. Confirm success toast appears and UI resets

## Acceptance Checklist

### ✅ Task 1.2.1 - Frontend Scaffolding
- [x] Project runs with `dev`, `build`, `preview` scripts
- [x] Tailwind utilities render correctly
- [x] shadcn/ui components (Button, Progress, Toaster) available
- [x] Toaster mounted globally with no console errors

### ✅ Task 1.2.2 - Routing & Upload
- [x] `/upload` route renders UploadPage.jsx
- [x] No hydration/console warnings
- [x] Toaster visible globally across routes

### ✅ Task 1.3.1 - File Selection UI
- [x] Users can select multiple images and see filenames + sizes
- [x] Non-image files blocked with clear warnings
- [x] Empty state visible when no files selected
- [x] Button/input accessible via keyboard with proper labels

### ✅ Task 1.4.1 - API Integration
- [x] `uploadImages(files, onProgress)` exists and returns parsed response data
- [x] Progress callback receives 0-100 during upload
- [x] Uses `VITE_API_BASE_URL` when present; otherwise defaults to localhost:8000
- [x] Body is `multipart/form-data` with `files` field name

### ✅ Task 1.4.2 - Upload Workflow & Progress
- [x] Clicking "Upload" triggers backend call and animates progress
- [x] Success toast shown; files/progress reset
- [x] Failure toast shown; UI re-enabled for retry
- [x] Duplicate submissions prevented during in-flight uploads

### ✅ Task 1.4.3 - Styling & Accessibility
- [x] Modern, clean page consistent with Tailwind + shadcn/ui
- [x] Keyboard navigation and focus states verified; inputs labeled
- [x] Frontend README includes env config and acceptance checklist
- [ ] (Optional) Drag-and-drop with previews

### ✅ Overall Cross-task Acceptance
- [x] `/upload` page exists and is reachable
- [x] Users can select and upload one or multiple images
- [x] Uploads hit backend and show progress + success/failure feedback  
- [x] Page uses shadcn/ui components and bootstrapped with Vite

## Troubleshooting

### Common Issues

**1. 404 Error on Upload**
- Ensure `VITE_API_BASE_URL` is set correctly in `.env`
- Verify backend server is running on the specified port
- Restart frontend server after changing environment variables

**2. 422 Unprocessable Entity**
- Check that backend expects `files` field name (not `files[]`)
- Verify FastAPI server is properly configured for multiple file uploads

**3. CORS Errors**
- Ensure backend has CORS middleware configured
- Check that frontend URL is allowed in backend CORS settings

**4. Build Errors**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version compatibility (16+)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is part of a training exercise and is for educational purposes.
