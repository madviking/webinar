import React from 'react'
import { Button, Group, LoadingOverlay, Paper, Table, Text, TextInput } from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { importInviteDefaults, listEmailTemplates, type EmailTemplateDTO } from '@/admin_cms/api/admin_cms.api'

export const EmailTemplatesPanel: React.FC = () => {
  const qc = useQueryClient()
  const [search, setSearch] = React.useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['admin-cms-email-templates', { search }],
    queryFn: () => listEmailTemplates({ skip: 0, limit: 100, search: search || undefined })
  })

  const importMut = useMutation({
    mutationFn: importInviteDefaults,
    onSuccess: () => {
      notifications.show({ title: 'Imported', message: 'Invite email template imported.', color: 'green' })
      qc.invalidateQueries({ queryKey: ['admin-cms-email-templates'] })
    },
    onError: (e: any) => {
      notifications.show({ title: 'Error', message: e?.response?.data?.detail || 'Failed to import template', color: 'red' })
    }
  })

  const items = data || []

  return (
    <Paper withBorder p="md" radius="md" pos="relative">
      <LoadingOverlay visible={isLoading} />
      <Group justify="space-between" mb="md">
        <Group>
          <Text fw={600}>Email Templates</Text>
          <Text size="sm" c="dimmed">Manage CMS email templates</Text>
        </Group>
        <Group>
          <TextInput placeholder="Search name..." value={search} onChange={(e) => setSearch(e.currentTarget.value)} />
          <Button variant="light" loading={importMut.isPending} onClick={() => importMut.mutate()}>Import Invite Default</Button>
        </Group>
      </Group>

      <Table striped highlightOnHover withTableBorder stickyHeader stickyHeaderOffset={0}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th style={{ width: 80 }}>ID</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Category</Table.Th>
            <Table.Th>Subject</Table.Th>
            <Table.Th style={{ width: 100 }}>Active</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {items.map((it: EmailTemplateDTO) => (
            <Table.Tr key={it.id}>
              <Table.Td>{it.id}</Table.Td>
              <Table.Td>{it.name}</Table.Td>
              <Table.Td>{it.category}</Table.Td>
              <Table.Td>
                <Text size="sm" lineClamp={1} title={it.subject_template}>{it.subject_template}</Text>
              </Table.Td>
              <Table.Td>{it.is_active ? 'Yes' : 'No'}</Table.Td>
            </Table.Tr>
          ))}
          {items.length === 0 && !isLoading && (
            <Table.Tr>
              <Table.Td colSpan={5}><Text size="sm" c="dimmed">No templates found</Text></Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>
    </Paper>
  )
}

