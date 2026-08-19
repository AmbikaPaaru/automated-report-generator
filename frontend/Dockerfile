# Frontend image: Next.js standalone build.
#
# NEXT_PUBLIC_API_BASE_URL is baked in at BUILD time, not runtime -- Next.js inlines
# every NEXT_PUBLIC_* var into the client bundle when `next build` runs, so it has to
# be passed as a build ARG (see docker-compose.yml's `build.args`), not just an
# `environment:` entry on the container (that would be too late).

FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
RUN npm run build

FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
