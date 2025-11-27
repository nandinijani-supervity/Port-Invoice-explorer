// frontend/src/app/api/auth/[...nextauth]/route.ts
import NextAuth, { AuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

const isAuthDebug = process.env.SUPERVITY_AUTH_DEBUG === 'true'

function log(message: string, data?: object) {
  if (isAuthDebug) {
    const logData = data ? JSON.stringify(data, null, 2) : ''
    console.log(
      `[AUTH_DEBUG | NextAuth] ${new Date().toISOString()}: ${message}\n${logData}`
    )
  }
}

const authOptions: AuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Demo Access',
      credentials: {},
      async authorize() {
        // Return hardcoded demo user
        return {
          id: '1',
          name: 'Demo Admin',
          email: 'admin@example.com',
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // Initial sign in
      if (user) {
        log('Initial sign-in flow. Demo user authenticated.', {
          user: user,
        })
        token.id = user.id
        token.name = user.name
        token.email = user.email
        return token
      }
      // Return token as is
      return token
    },
    async session({ session, token }) {
      log('Session callback triggered.')
      if (token) {
        session.user = {
          ...session.user,
          id: token.id as string,
          name: token.name as string,
          email: token.email as string,
        } as typeof session.user & { id: string }
      }
      log('Returning session object to client.', {
        user: session.user,
      })
      return session
    },
    async redirect({ url, baseUrl }) {
      log(`Redirect callback triggered. url: ${url}, baseUrl: ${baseUrl}`)
      
      // Handle base path correctly
      const basePath = process.env.NEXT_PUBLIC_BASE_PATH || ''
      
      // Allows relative callback URLs
      if (url.startsWith('/')) {
        // Check if url already starts with basePath to avoid duplication
        if (basePath && url.startsWith(basePath)) {
          return `${baseUrl}${url}`
        }
        return `${baseUrl}${basePath}${url}`
      }
      // Allows callback URLs on the same origin
      else if (new URL(url).origin === baseUrl) return url
      // Default redirect to base path
      return `${baseUrl}${basePath}`
    },
  },
  events: {
    async signIn({ user }) {
      log('✅ User signed in successfully (Demo Mode).', {
        user: user,
      })
    },
    async signOut() {
      log('User signing out (Demo Mode).')
    },
  },
  pages: {
    signIn: `${process.env.NEXT_PUBLIC_BASE_PATH || ''}/api/auth/signin`,
  },
  secret: process.env.NEXTAUTH_SECRET,
  debug: process.env.SUPERVITY_AUTH_DEBUG === 'true',
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
