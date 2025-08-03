import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { discussionsApi, type GetDiscussionsParams, type CreateDiscussionParams, type UpdateDiscussionParams } from '@/lib/api/discussions';

export function useDiscussions(params: GetDiscussionsParams = {}) {
    return useQuery({
        queryKey: ['discussions', params],
        queryFn: () => discussionsApi.getDiscussions(params),
        staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    });
}

export function useDiscussion(id: number) {
    return useQuery({
        queryKey: ['discussion', id],
        queryFn: () => discussionsApi.getDiscussion(id),
        staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
        enabled: !!id, // Only run if id exists
    });
}

export function useCreateDiscussion() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: CreateDiscussionParams) => discussionsApi.createDiscussion(data),
        onSuccess: () => {
            // Invalidate discussions list to refetch
            queryClient.invalidateQueries({ queryKey: ['discussions'] });
        },
    });
}

export function useUpdateDiscussion(id: number) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: UpdateDiscussionParams) => discussionsApi.updateDiscussion(id, data),
        onSuccess: (updatedDiscussion) => {
            // Update the specific discussion in the cache
            queryClient.setQueryData(['discussion', id], updatedDiscussion);
            // Invalidate discussions list to refetch
            queryClient.invalidateQueries({ queryKey: ['discussions'] });
        },
    });
}

export function useDeleteDiscussion() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => discussionsApi.deleteDiscussion(id),
        onSuccess: () => {
            // Invalidate discussions list to refetch
            queryClient.invalidateQueries({ queryKey: ['discussions'] });
        },
    });
}
