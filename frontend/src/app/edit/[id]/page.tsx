import { EditorClient } from "@/components/editor/EditorClient";

export default async function EditPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <EditorClient tailoredResumeId={id} />;
}
