# Frontend

This frontend is a Next.js app for the nurse rostering prototype.

It is the UI layer for looking at projects, editing planning data, starting solver runs, and opening returned solutions.

## What the UI does

The current frontend is centered around two main views:

- a project list page
- a project detail page

The root route redirects to `/projects`, so the project list is the real entry point.

From here, the UI lets you move into a single project and work with its rostering data.

Inside a project, the code shows controls and views for things like:

- nurses
- shifts
- shift types
- planning horizon
- constraints
- solver choice
- time limit
- jobs
- solutions
- variable fixing

The frontend is not just a read-only dashboard. It is also the editor/control surface for building and solving an instance.

## Main folders

### `src/app/`

This contains the routes.

Important pages are:

- `page.tsx` - redirects to `/projects`
- `projects/page.tsx` - project overview list
- `projects/[projectId]/page.tsx` - single project workspace

There is also an `api/` folder with frontend-side API files used by the UI.

### `src/components/`

This is where most of the UI lives.

The structure is split into:

- `common/` - dialogs and editors
- `layout/` - larger page sections like sidebar and jobs view
- `rostering/` - nurse/shift/solution/solver components
- `ui/` - reusable smaller UI pieces

A lot of the actual project interaction happens through these dialog-based components.

### `src/store/`

The frontend uses Zustand for state.

There are stores for things like:

- selected project
- project list
- nurses and shifts
- current instance
- solver settings
- messages / job ids
- loaded solutions

Meaning the app keeps a fair amount of working state on the client side.

### `src/hooks/`

The hooks folder is used for loading data into the stores.


## API flow

The frontend-side API helpers call routes under `/api/...`.

For example, the project API helper covers create, read, update, and delete for projects.

The jobs helper also reads finished jobs from a webhook/job-status route.

On the project page, the code polls for finished jobs and then fetches the related solution data.

The UI is built around asynchronous solver runs instead of assuming an instant result.

# Setup

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

#### Environment Configuration
To connect with the FastAPI, you have to provide a URL in an environment file. To do so, follow these steps:
1. In this folder (frontend/), create a .env file (touch .env)
2. copy the contents from the .env.example file.
3. That is it. The URL in the example file is the URL of the FastAPI




First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
