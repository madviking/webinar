import React from 'react'
import { Badge, Button, Group, LoadingOverlay, Modal, Paper, Table, Text, TextInput, Textarea } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { importInviteDefaults, importAllEmailDefaults } from '@/admin_cms/api/admin_cms.api'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { createEmailTemplate, deleteEmailTemplate, getTemplateVariables, listEmailTemplates, updateEmailTemplate, type EmailTemplateDTO } from '@/admin_cms/api/admin_cms.api'

interface EmailFormValues {
  name: string
  category: string
  subject_template: string
  body_html: string
  variables: string
}

const EmailTemplateForm: React.FC<{
  initial?: Partial<EmailFormValues>
  isEdit?: boolean
  variablesHints?: string[]
  onCancel: () => void
  onSubmit: (values: EmailFormValues) => void
  submitting?: boolean
}> = ({ initial, isEdit, variablesHints, onCancel, onSubmit, submitting }) => {
  const [name, setName] = React.useState(initial?.name ?? '')
  const [category, setCategory] = React.useState(initial?.category ?? '')
  const [subject, setSubject] = React.useState(initial?.subject_template ?? '')
  const [body, setBody] = React.useState(initial?.body_html ?? '')
  const [varsStr, setVarsStr] = React.useState(initial?.variables ?? '')

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit({ name: name.trim(), category: category.trim(), subject_template: subject, body_html: body, variables: varsStr }) }}>
      <Group grow>
        <TextInput label="Name" placeholder="invitation" value={name} onChange={(e) => setName(e.currentTarget.value)} required disabled={!!isEdit} />
        <TextInput label="Category" placeholder="invitation" value={category} onChange={(e) => setCategory(e.currentTarget.value)} required />
      </Group>
      <TextInput label="Subject" placeholder="Welcome, {{user_name}}" value={subject} onChange={(e) => setSubject(e.currentTarget.value)} required mt="md" />
      <Textarea label="Body HTML" placeholder="<h1>Hello {{user_name}}</h1>" value={body} onChange={(e) => setBody(e.currentTarget.value)} autosize minRows={8} required mt="md" />
      <TextInput label="Variables (comma separated)" placeholder="user_name, accept_url" value={varsStr} onChange={(e) => setVarsStr(e.currentTarget.value)} mt="md" />
      {variablesHints && variablesHints.length > 0 && (
        <Group gap={6} mt="xs">{variablesHints.map(v => <Badge key={v} variant="light">{v}</Badge>)}</Group>
      )}
      <Group justify="flex-end" mt="lg">
        <Button variant="default" onClick={onCancel} disabled={submitting}>Cancel</Button>
        <Button type="submit" loading={submitting}>Save</Button>
      </Group>
    </form>
  )}

export const EmailTemplatesTable: React.FC = () => {
  const qc = useQueryClient()
  const [createOpen, setCreateOpen] = React.useState(false)
  const [editTarget, setEditTarget] = React.useState<EmailTemplateDTO | null>(null)
  const [search, setSearch] = React.useState('')

  const { data, isLoading } = useQuery({ queryKey: ['cms-email-templates'], queryFn: () => listEmailTemplates({ skip: 0, limit: 200 }) })
  const { data: varsMap } = useQuery({ queryKey: ['cms-template-variables'], queryFn: () => getTemplateVariables() })

  const createMut = useMutation({
    mutationFn: (values: EmailFormValues) => createEmailTemplate({
      name: values.name,
      category: values.category,
      subject_template: values.subject_template,
      body_html: values.body_html,
      variables: values.variables ? values.variables.split(',').map(s => s.trim()).filter(Boolean) : [],
      is_active: true,
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['cms-email-templates'] }); setCreateOpen(false) }
  })

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: number, values: EmailFormValues }) => updateEmailTemplate(id, {
      category: values.category,
      subject_template: values.subject_template,
      body_html: values.body_html,
      variables: values.variables ? values.variables.split(',').map(s => s.trim()).filter(Boolean) : [],
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['cms-email-templates'] }); setEditTarget(null) }
  })

  const deleteMut = useMutation({ mutationFn: deleteEmailTemplate, onSuccess: () => qc.invalidateQueries({ queryKey: ['cms-email-templates'] }) })

  const items = (data || []).filter(it => !search || it.name.includes(search) || it.category.toLowerCase().includes(search.toLowerCase()))

  const varsHintsFor = (category?: string) => (category && varsMap ? varsMap[category] : undefined)

  return (
    <Paper withBorder p="md" radius="md" pos="relative">
      <LoadingOverlay visible={isLoading} />
      <Group justify="space-between" mb="md">
        <Text fw={600}>Email Templates</Text>
        <Group>
          <TextInput placeholder="Search by name or category..." value={search} onChange={(e) => setSearch(e.currentTarget.value)} />
          <Button onClick={() => setCreateOpen(true)}>New Email Template</Button>
          <Button variant="light" onClick={async () => {
            try {
              await importInviteDefaults()
              notifications.show({ title: 'Imported', message: 'Invite email template imported.', color: 'green' })
              qc.invalidateQueries({ queryKey: ['cms-email-templates'] })
            } catch (e: any) {
              notifications.show({ title: 'Error', message: e?.response?.data?.detail || 'Failed to import default invite template', color: 'red' })
            }
          }}>Import Invite Default</Button>
          <Button variant="default" onClick={async () => {
            try {
              await importAllEmailDefaults()
              notifications.show({ title: 'Imported', message: 'All missing email templates imported.', color: 'green' })
              qc.invalidateQueries({ queryKey: ['cms-email-templates'] })
            } catch (e: any) {
              notifications.show({ title: 'Error', message: e?.response?.data?.detail || 'Failed to import default email templates', color: 'red' })
            }
          }}>Import All Defaults</Button>
        </Group>
      </Group>

      <Table striped highlightOnHover withTableBorder stickyHeader stickyHeaderOffset={0}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th style={{ width: 80 }}>ID</Table.Th>
            <Table.Th>Name</Table.Th>
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
              <Table.Td>{it.category}</Table.Td>
              <Table.Td>
                <Text size="sm" c="dimmed" lineClamp={1}>{it.subject_template}</Text>
              </Table.Td>
              <Table.Td>
                <Group gap={6}>{it.variables?.map(v => <Badge key={v} variant="light">{v}</Badge>)}</Group>
              </Table.Td>
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
              <Table.Td colSpan={6}><Text size="sm" c="dimmed">No email templates found</Text></Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>

      {/* Create */}
      <Modal opened={createOpen} onClose={() => setCreateOpen(false)} title="New Email Template" size="lg">
        <EmailTemplateForm
          variablesHints={varsHintsFor(undefined)}
          onCancel={() => setCreateOpen(false)}
          onSubmit={(values) => createMut.mutate(values)}
          submitting={createMut.isPending}
        />
      </Modal>

      {/* Edit */}
      <Modal opened={!!editTarget} onClose={() => setEditTarget(null)} title={`Edit: ${editTarget?.name}`} size="lg">
        {editTarget && (
          <EmailTemplateForm
            initial={{ name: editTarget.name, category: editTarget.category, subject_template: editTarget.subject_template, body_html: editTarget.body_html, variables: (editTarget.variables || []).join(', ') }}
            isEdit
            variablesHints={varsHintsFor(editTarget.category)}
            onCancel={() => setEditTarget(null)}
            onSubmit={(values) => updateMut.mutate({ id: editTarget.id, values })}
            submitting={updateMut.isPending}
          />
        )}
      </Modal>
    </Paper>
  )
}
