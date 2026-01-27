import React, { useState } from 'react'
import { ContentBlocksTable } from '@/admin_cms/components/ContentBlocksTable'
import { EmailTemplatesTable } from '@/admin_cms/components/EmailTemplatesTable'
import { NotificationTemplatesTable } from '@/admin_cms/components/NotificationTemplatesTable'
import { AdminPageLayout } from '@/admin_framework/components/AdminPageLayout'
import { DashboardBannerManager } from '@/dashboard_banners/components/DashboardBannerManager'

export const AdminCMSPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('email')

  return (
    <AdminPageLayout
      title="CMS"
      description="Manage content blocks and notification templates."
      tabs={{
        value: activeTab,
        onChange: setActiveTab,
        items: [
          { value: 'blocks', label: 'Content Blocks' },
          { value: 'email', label: 'Email Templates' },
          { value: 'notifications', label: 'Notification Templates' },
          { value: 'banners', label: 'System Banners' },
        ],
      }}
    >
      {activeTab === 'blocks' ? <ContentBlocksTable /> : null}
      {activeTab === 'email' ? <EmailTemplatesTable /> : null}
      {activeTab === 'notifications' ? <NotificationTemplatesTable /> : null}
      {activeTab === 'banners' ? <DashboardBannerManager scope={{ kind: 'system' }} /> : null}
    </AdminPageLayout>
  )
}

export default AdminCMSPage
