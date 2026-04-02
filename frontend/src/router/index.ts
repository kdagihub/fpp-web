import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const PublicLayout = () => import('@/layouts/PublicLayout.vue')
const AdminLayout = () => import('@/layouts/AdminLayout.vue')

/* ── Public views ── */
const HomeView = () => import('@/views/public/HomeView.vue')
const AboutView = () => import('@/views/public/AboutView.vue')
const NewsView = () => import('@/views/public/NewsView.vue')
const NewsDetailView = () => import('@/views/public/NewsDetailView.vue')
const JoinView = () => import('@/views/public/JoinView.vue')
const ContactView = () => import('@/views/public/ContactView.vue')

/* ── Auth views ── */
const LoginView = () => import('@/views/auth/LoginView.vue')
const VerifyEmailView = () => import('@/views/auth/VerifyEmailView.vue')
const PasswordResetView = () => import('@/views/auth/PasswordResetView.vue')
const PasswordResetConfirmView = () => import('@/views/auth/PasswordResetConfirmView.vue')

/* ── Admin views ── */
const AdminDashboardView = () => import('@/views/admin/DashboardView.vue')
const AdminMembersView = () => import('@/views/admin/MembersView.vue')
const AdminMemberDetailView = () => import('@/views/admin/MemberDetailView.vue')
const AdminArticlesView = () => import('@/views/admin/ArticlesView.vue')
const AdminArticleEditorView = () => import('@/views/admin/ArticleEditorView.vue')
const AdminContactsView = () => import('@/views/admin/ContactsView.vue')
const AdminSettingsView = () => import('@/views/admin/SettingsView.vue')
const AdminAuditLogView = () => import('@/views/admin/AuditLogView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(_to, _from, savedPosition) {
    return savedPosition ?? { top: 0 }
  },
  routes: [
    /* ── Public ── */
    {
      path: '/',
      component: PublicLayout,
      children: [
        { path: '', name: 'home', component: HomeView },
        { path: 'a-propos', name: 'about', component: AboutView },
        { path: 'actualites', name: 'news', component: NewsView },
        { path: 'actualites/:slug', name: 'news-detail', component: NewsDetailView, props: true },
        { path: 'adherer', name: 'join', component: JoinView },
        { path: 'contact', name: 'contact', component: ContactView },
      ],
    },

    /* ── Auth (no layout chrome) ── */
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true },
    },
    {
      path: '/verify-email',
      name: 'verify-email',
      component: VerifyEmailView,
    },
    {
      path: '/password-reset',
      name: 'password-reset',
      component: PasswordResetView,
      meta: { guest: true },
    },
    {
      path: '/password-reset/confirm',
      name: 'password-reset-confirm',
      component: PasswordResetConfirmView,
      meta: { guest: true },
    },

    /* ── Admin ── */
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: AdminDashboardView,
          meta: { permission: 'can_view_dashboard' },
        },
        {
          path: 'membres',
          name: 'admin-members',
          component: AdminMembersView,
          meta: { permission: 'can_view_members' },
        },
        {
          path: 'membres/:id',
          name: 'admin-member-detail',
          component: AdminMemberDetailView,
          props: true,
          meta: { permission: 'can_view_members' },
        },
        {
          path: 'articles',
          name: 'admin-articles',
          component: AdminArticlesView,
          meta: { permission: 'can_create_article' },
        },
        {
          path: 'articles/new',
          name: 'admin-article-new',
          component: AdminArticleEditorView,
          meta: { permission: 'can_create_article' },
        },
        {
          path: 'articles/:id/edit',
          name: 'admin-article-edit',
          component: AdminArticleEditorView,
          props: true,
          meta: { permission: 'can_edit_article' },
        },
        {
          path: 'contacts',
          name: 'admin-contacts',
          component: AdminContactsView,
          meta: { permission: 'can_manage_contacts' },
        },
        {
          path: 'parametres',
          name: 'admin-settings',
          component: AdminSettingsView,
          meta: { permission: 'can_manage_settings' },
        },
        {
          path: 'audit',
          name: 'admin-audit',
          component: AdminAuditLogView,
          meta: { permission: 'can_view_audit_log' },
        },
      ],
    },

    /* ── 404 ── */
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

/* ── Navigation guards ── */

router.beforeEach(async (to: RouteLocationNormalized) => {
  const auth = useAuthStore()

  if (!auth.initialized) {
    await auth.init()
  }

  // Guest-only routes (login, register) — redirect if already logged in
  if (to.meta.guest && auth.isAuthenticated) {
    return auth.isAdmin ? '/admin/dashboard' : '/'
  }

  // Protected routes — redirect if not authenticated
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // Admin routes — redirect if not staff
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return '/'
  }

  // Permission-based routes
  if (to.meta.permission && typeof to.meta.permission === 'string') {
    if (!auth.hasPermission(to.meta.permission)) {
      return '/admin/dashboard'
    }
  }
})

export default router
