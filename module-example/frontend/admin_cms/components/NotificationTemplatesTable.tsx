import React from 'react'
import { Badge, Button, Group, LoadingOverlay, Modal, Paper, Select, Table, Text, TextInput, Textarea, Switch } from '@mantine/core'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createNotificationTemplate, deleteNotificationTemplate, importAllNotificationDefaults, listNotificationTemplates, updateNotificationTemplate, type NotificationTemplateDTO } from '@/admin_cms/api/admin_cms.api'
import { notifications } from '@mantine/notifications'

interface FormValues {
  name: string
  template_type: 'email' | 'slack'
  category: string
  subject_template?: string
  body_template: string
  variables: string
  is_active: boolean
  is_default: boolean
}

const NotificationTemplateForm: React.FC<{
  initial?: Partial<FormValues>
  isEdit?: boolean
  onCancel: () => void
  onSubmit: (values: FormValues) => void
  submitting?: boolean
}> = ({ initial, isEdit, onCancel, onSubmit, submitting }) => {
  const [name, setName] = React.useState(initial?.name ?? '')
  const [type, setType] = React.useState<'email' | 'slack'>((initial?.template_type as any) ?? 'email')
  const [category, setCategory] = React.useState(initial?.category ?? '')
  const [subject, setSubject] = React.useState(initial?.subject_template ?? '')
  const [body, setBody] = React.useState(initial?.body_template ?? '')
  const [varsStr, setVarsStr] = React.useState(initial?.variables ?? '')
  const [isActive, setIsActive] = React.useState(initial?.is_active ?? true)
  const [isDefault, setIsDefault] = React.useState(initial?.is_default ?? false)

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit({ name: name.trim(), template_type: type, category: category.trim(), subject_template: subject || undefined, body_template: body, variables: varsStr, is_active: isActive, is_default: isDefault }) }}>
      <Group grow>
        <TextInput label="Name" placeholder="daily_digest_email" value={name} onChange={(e) => setName(e.currentTarget.value)} required disabled={!!isEdit} />
        <Select label="Type" data={[{ value: 'email', label: 'email' }, { value: 'slack', label: 'slack' }]} value={type} onChange={(v) => setType((v as 'email'|'slack') ?? 'email')} required disabled={!!isEdit} />
        <TextInput label="Category" placeholder="digest" value={category} onChange={(e) => setCategory(e.currentTarget.value)} required />
      </Group>
      {type === 'email' && (
        <TextInput label="Subject" placeholder="Daily Digest - {{date}}" value={subject} onChange={(e) => setSubject(e.currentTarget.value)} required mt="md" />
      )}
      <Textarea label="Body" placeholder="Hello {{user_name}}..." value={body} onChange={(e) => setBody(e.currentTarget.value)} autosize minRows={6} required mt="md" />
      <TextInput label="Variables (comma separated)" placeholder="user_name, date, ..." value={varsStr} onChange={(e) => setVarsStr(e.currentTarget.value)} mt="md" />
      <Group mt="md">
        <Switch label="Active" checked={isActive} onChange={(e) => setIsActive(e.currentTarget.checked)} />
        <Switch label="Default" checked={isDefault} onChange={(e) => setIsDefault(e.currentTarget.checked)} />
      </Group>
      <Group justify="flex-end" mt="lg">
        <Button variant="default" onClick={onCancel} disabled={submitting}>Cancel</Button>
        <Button type="submit" loading={submitting}>Save</Button>
      </Group>
    </form>
  )
}

export const NotificationTemplatesTable: React.FC = () => {
  const qc = useQueryClient()
  const [createOpen, setCreateOpen] = React.useState(false)
  const [editTarget, setEditTarget] = React.useState<NotificationTemplateDTO | null>(null)
  const [search, setSearch] = React.useState('')
  const [filterType, setFilterType] = React.useState<'email'|'slack'|'all'>('all')

  const { data, isLoading } = useQuery({ queryKey: ['cms-notification-templates', { filterType }], queryFn: () => listNotificationTemplates({ template_type: filterType === 'all' ? undefined : filterType }) })

  const createMut = useMutation({
    mutationFn: (values: FormValues) => createNotificationTemplate({
      name: values.name,
      template_type: values.template_type,
      category: values.category,
      subject_template: values.subject_template,
      body_template: values.body_template,
      variables: values.variables ? values.variables.split(',').map(s => s.trim()).filter(Boolean) : [],
      is_active: values.is_active,
      is_default: values.is_default,
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['cms-notification-templates'] }); setCreateOpen(false) }
  })

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: number, values: FormValues }) => updateNotificationTemplate(id, {
      category: values.category,
      subject_template: values.subject_template,
      body_template: values.body_template,
      variables: values.variables ? values.variables.split(',').map(s => s.trim()).filter(Boolean) : [],
      is_active: values.is_active,
      is_default: values.is_default,
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['cms-notification-templates'] }); setEditTarget(null) }
  })

  const deleteMut = useMutation({ mutationFn: deleteNotificationTemplate, onSuccess: () => qc.invalidateQueries({ queryKey: ['cms-notification-templates'] }) })

  const items = (data || []).filter(it => !search || it.name.includes(search) || it.category.toLowerCase().includes(search.toLowerCase()))

  return (
    <Paper withBorder p="md" radius="md" pos="relative">
      <LoadingOverlay visible={isLoading} />
      <Group justify="space-between" mb="md">
        <Text fw={600}>Notification Templates</Text>
        <Group>
          <Select data={[{value:'all',label:'All'},{value:'email',label:'Email'},{value:'slack',label:'Slack'}]} value={filterType} onChange={(v) => setFilterType((v as any) ?? 'all')} style={{ width: 120 }} />
          <TextInput placeholder="Search by name/category..." value={search} onChange={(e) => setSearch(e.currentTarget.value)} />
          <Button onClick={() => setCreateOpen(true)}>New Notification Template</Button>
          <Button variant="light" onClick={async () => {
            try {
              await importAllNotificationDefaults()
              notifications.show({ title: 'Imported', message: 'All missing notification templates imported.', color: 'green' })
              qc.invalidateQueries({ queryKey: ['cms-notification-templates'] })
            } catch (e: any) {
              notifications.show({ title: 'Error', message: e?.response?.data?.detail || 'Failed to import notification defaults', color: 'red' })
            }
          }}>Import Missing Defaults</Button>
        </Group>
      </Group>

      <Table striped highlightOnHover withTableBorder stickyHeader stickyHeaderOffset={0}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th style={{ width: 80 }}>ID</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Type</Table.Th>
            <Table.Th>Category</Table.Th>
            <Table.Th>Subject</Table.Th>
            <Table.Th>Variables</Table.Th>
            <Table.Th style={{ width: 220 }}></Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {items.map(it => (
            <Table.Tr key={it.id}>
              <Table.Td>{it.id}</Table.Td>
              <Table.Td>{it.name}</Table.Td>
              <Table.Td>{it.template_type}</Table.Td>
              <Table.Td>{it.category}</Table.Td>
              <Table.Td><Text size="sm" c="dimmed" lineClamp={1}>{it.subject_template || '-'}</Text></Table.Td>
              <Table.Td><Group gap={6}>{(it.variables || []).map(v => <Badge key={v} variant="light">{v}</Badge>)}</Group></Table.Td>
              <Table.Td>
                <Group justify="end" gap="xs">
                  <Button size="xs" variant="light" onClick={() => setEditTarget(it)}>Edit</Button>
                  <Button size="xs" color="gray" variant="outline" loading={deleteMut.isPending} onClick={() => deleteMut.mutate(it.id)}>Delete</Button>
                </Group>
              </Table.Td>
            </Table.Tr>
          ))}
          {items.length === 0 && !isLoading && (
            <Table.Tr>
              <Table.Td colSpan={7}><Text size="sm" c="dimmed">No notification templates found</Text></Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>

      {/* Create */}
      <Modal opened={createOpen} onClose={() => setCreateOpen(false)} title="New Notification Template" size="lg">
        <NotificationTemplateForm onCancel={() => setCreateOpen(false)} onSubmit={(values) => createMut.mutate(values)} submitting={createMut.isPending} />
      </Modal>

      {/* Edit */}
      <Modal opened={!!editTarget} onClose={() => setEditTarget(null)} title={`Edit: ${editTarget?.name}`} size="lg">
        {editTarget && (
          <NotificationTemplateForm
            initial={{
              name: editTarget.name,
              template_type: editTarget.template_type,
              category: editTarget.category,
              subject_template: editTarget.subject_template,
              body_template: editTarget.body_template,
              variables: (editTarget.variables || []).join(', '),
              is_active: editTarget.is_active,
              is_default: editTarget.is_default,
            }}
            isEdit
            onCancel={() => setEditTarget(null)}
            onSubmit={(values) => updateMut.mutate({ id: editTarget.id, values })}
            submitting={updateMut.isPending}
          />
        )}
      </Modal>
    </Paper>
  )
}
