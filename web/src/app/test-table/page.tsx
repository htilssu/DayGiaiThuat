import { TableDemo } from '@/components/ui/TableDemo';

export default function TableTestPage() {
    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-6xl mx-auto">
                <div className="bg-white rounded-lg shadow-lg p-8">
                    <h1 className="text-3xl font-bold mb-6 text-center text-gray-900">
                        Table Markdown Rendering Test
                    </h1>
                    <TableDemo />
                </div>
            </div>
        </div>
    );
}
