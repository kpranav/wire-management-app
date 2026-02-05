# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build arguments for environment variables
ARG VITE_API_URL
ARG VITE_WS_URL
ARG VITE_FEATURE_CSV_EXPORT=false
ARG VITE_FEATURE_ADVANCED_FILTERS=true
ARG VITE_FEATURE_AUDIT_LOG=false

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL
ENV VITE_FEATURE_CSV_EXPORT=$VITE_FEATURE_CSV_EXPORT
ENV VITE_FEATURE_ADVANCED_FILTERS=$VITE_FEATURE_ADVANCED_FILTERS
ENV VITE_FEATURE_AUDIT_LOG=$VITE_FEATURE_AUDIT_LOG

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
