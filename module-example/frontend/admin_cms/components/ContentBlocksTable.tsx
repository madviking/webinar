import React from 'react'
import { Button, Group, LoadingOverlay, Modal, Paper, Table, Text, TextInput, Textarea, Badge, Select } from '@mantine/core'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { createContentBlock, deleteContentBlock, listContentBlocks, updateContentBlock, importAllContentBlockDefaults, loadTermsDefaultBlock, type ContentBlockDTO } from '@/admin_cms/api/admin_cms.api'

interface BlockFormValues {
  key: string
  category: string
  title: string
  html_content: string
  description?: string
  variables: string
}

const ContentBlockForm: React.FC<{
  initial?: Partial<BlockFormValues>
  isEdit?: boolean
  onCancel: () => void
  onSubmit: (values: BlockFormValues) => void
  submitting?: boolean
}> = ({ initial, isEdit, onCancel, onSubmit, submitting }) => {
  const [key, setKey] = React.useState(initial?.key ?? '')
  const [category, setCategory] = React.useState(initial?.category ?? 'content')
  const [title, setTitle] = React.useState(initial?.title ?? '')
  const [html, setHtml] = React.useState(initial?.html_content ?? '')
  const [description, setDescription] = React.useState(initial?.description ?? '')
  const [varsStr, setVarsStr] = React.useState(initial?.variables ?? '')

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit({ key: key.trim(), category: category.trim() || 'content', title: title.trim(), html_content: html, description: description || undefined, variables: varsStr }) }}>
      <Group grow>
        <TextInput label="Key" placeholder="dashboard_intro" value={key} onChange={(e) => setKey(e.currentTarget.value)} required disabled={!!isEdit} />
        <TextInput label="Category" placeholder="content, product_tour, ..." value={category} onChange={(e) => setCategory(e.currentTarget.value)} required />
        <TextInput label="Title" placeholder="Dashboard Intro" value={title} onChange={(e) => setTitle(e.currentTarget.value)} required />
      </Group>
      <TextInput label="Description" placeholder="Optional description" value={description} onChange={(e) => setDescription(e.currentTarget.value)} mt="md" />
      <Textarea label="HTML Content" placeholder="<p>...</p>" value={html} onChange={(e) => setHtml(e.currentTarget.value)} autosize minRows={8} required mt="md" />
      <TextInput label="Variables (comma separated)" placeholder="user_name, accept_url" value={varsStr} onChange={(e) => setVarsStr(e.currentTarget.value)} mt="md" />
      <Group justify="flex-end" mt="lg">
        <Button variant="default" onClick={onCancel} disabled={submitting}>Cancel</Button>
        <Button type="submit" loading={submitting}>Save</Button>
      </Group>
    </form>
  )
}

export const ContentBlocksTable: React.FC = () => {
  const qc = useQueryClient()
  const [createOpen, setCreateOpen] = React.useState(false)
  const [editTarget, setEditTarget] = React.useState<ContentBlockDTO | null>(null)
  const [search, setSearch] = React.useState('')
  const [filterCategory, setFilterCategory] = React.useState<string>('all')

  const requestedCategory = filterCategory === 'all' ? undefined : filterCategory
  const { data, isLoading } = useQuery({
    queryKey: ['cms-blocks', { category: requestedCategory }],
    queryFn: () => listContentBlocks(requestedCategory ? { category: requestedCategory } : undefined),
  })

  const createMut = useMutation({
    mutationFn: (values: BlockFormValues) => createContentBlock({
      key: values.key,
      category: values.category || 'content',
      title: values.title,
      html_content: values.html_content,
      description: values.description,
      variables: values.variables ? values.variables.split(',').map(s => s.trim()).filter(Boolean) : [],
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['cms-blocks'] }); setCreateOpen(false) }
  })

  const updateMut = useMutation({
    mutationFn: ({ id, values }: { id: number, values: BlockFormValues }) => updateContentBlock(id, {
      category: values.category || undefined,
      title: values.title,
      html_content: values.html_content,
      description: values.description,
      variables: values.variables ? values.variables.split(',').map(s => s.trim()).filter(Boolean) : [],
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['cms-blocks'] }); setEditTarget(null) }
  })

  const deleteMut = useMutation({ mutationFn: deleteContentBlock, onSuccess: () => qc.invalidateQueries({ queryKey: ['cms-blocks'] }) })
  const importDefaultsMut = useMutation({ mutationFn: importAllContentBlockDefaults, onSuccess: () => qc.invalidateQueries({ queryKey: ['cms-blocks'] }) })
  const loadTermsMut = useMutation({ mutationFn: loadTermsDefaultBlock, onSuccess: () => qc.invalidateQueries({ queryKey: ['cms-blocks'] }) })

  const categoryOptions = React.useMemo(() => {
    const preset = new Set<string>(['content', 'product_tour'])
    for (const blk of data || []) {
      if (blk.category) preset.add(blk.category)
    }
    return Array.from(preset)
  }, [data])

  const items = (data || []).filter(it => {
    const matchesSearch = !search || it.key.includes(search) || it.title.toLowerCase().includes(search.toLowerCase()) || (it.category || '').toLowerCase().includes(search.toLowerCase())
    const matchesCategory = filterCategory === 'all' || it.category === filterCategory
    return matchesSearch && matchesCategory
  })

  return (
    <Paper withBorder p="md" radius="md" pos="relative">
      <LoadingOverlay visible={isLoading} />
      <Group justify="space-between" mb="md">
        <Text fw={600}>Content Blocks</Text>
        <Group>
          <Button variant="light" color="gray" loading={importDefaultsMut.isPending} onClick={() => importDefaultsMut.mutate()}>Import Missing</Button>
          <Button variant="light" color="gray" loading={loadTermsMut.isPending} onClick={() => loadTermsMut.mutate()}>Load Terms Default</Button>
          <Select
            placeholder="All categories"
            value={filterCategory}
            onChange={(val) => setFilterCategory(val || 'all')}
            data={[{ value: 'all', label: 'All categories' }, ...categoryOptions.map(v => ({ value: v, label: v }))]}
            searchable
            clearable
            style={{ minWidth: 180 }}
          />
          <TextInput placeholder="Search key or title..." value={search} onChange={(e) => setSearch(e.currentTarget.value)} />
          <Button onClick={() => setCreateOpen(true)}>New Block</Button>
        </Group>
      </Group>

      <Table striped highlightOnHover withTableBorder stickyHeader stickyHeaderOffset={0}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th style={{ width: 80 }}>ID</Table.Th>
            <Table.Th>Key</Table.Th>
            <Table.Th>Category</Table.Th>
            <Table.Th>Title</Table.Th>
            <Table.Th>Variables</Table.Th>
            <Table.Th style={{ width: 220 }}></Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {items.map(it => (
            <Table.Tr key={it.id}>
              <Table.Td>{it.id}</Table.Td>
              <Table.Td>{it.key}</Table.Td>
              <Table.Td><Badge variant="light">{it.category}</Badge></Table.Td>
              <Table.Td>{it.title}</Table.Td>
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
              <Table.Td colSpan={5}><Text size="sm" c="dimmed">No content blocks found</Text></Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>

      {/* Create */}
      <Modal opened={createOpen} onClose={() => setCreateOpen(false)} title="New Content Block" size="lg">
        <ContentBlockForm onCancel={() => setCreateOpen(false)} onSubmit={(values) => createMut.mutate(values)} submitting={createMut.isPending} />
      </Modal>

      {/* Edit */}
      <Modal opened={!!editTarget} onClose={() => setEditTarget(null)} title={`Edit: ${editTarget?.key}`} size="lg">
        {editTarget && (
          <ContentBlockForm
            initial={{ key: editTarget.key, category: editTarget.category, title: editTarget.title, html_content: editTarget.html_content, description: editTarget.description ?? '', variables: (editTarget.variables || []).join(', ') }}
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
