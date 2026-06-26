import React, { useCallback, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  useTheme,
  useMediaQuery,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  FitScreen as FitScreenIcon,
} from '@mui/icons-material';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { PageHeader, StatCard } from '@/shared/components/ui';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/shared/components/loading';
import { useQueryPlan } from '@/lib/react-query';

interface ExecutionPlanNodeData {
  'Node ID'?: string;
  node_id?: string;
  'Node Type'?: string;
  node_type?: string;
  'Startup Cost'?: number;
  startup_cost?: number;
  'Total Cost'?: number;
  total_cost?: number;
  'Plan Rows'?: number;
  plan_rows?: number;
  'Actual Rows'?: number;
  actual_rows?: number;
  'Actual Loops'?: number;
  actual_loops?: number;
  'Actual Total Time'?: number;
  actual_total_time?: number;
  'Relation Name'?: string;
  relation_name?: string;
  Filter?: string;
  'Sort Key'?: string;
  sort_key?: string;
  'Join Type'?: string;
  join_type?: string;
  Plans?: ExecutionPlanNodeData[];
}

interface ExecutionPlanData {
  planWidth?: number;
  executionTimeMs?: number;
  format?: string;
  totalCost?: number;
  totalRows?: number;
  planJson?: ExecutionPlanNodeData | ExecutionPlanNodeData[];
}

interface PlanNode extends Node {
  data: {
    label: string;
    nodeType: string;
    startupCost: number;
    totalCost: number;
    planRows: number;
    actualRows?: number;
    actualLoops?: number;
    actualTotalTime?: number;
    relationName?: string;
    filter?: string;
    sortKey?: string;
    joinType?: string;
  };
}

export const ExecutionPlanViewerPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { id } = useParams<{ id: string }>();
  
  const { data, isLoading, error, refetch } = useQueryPlan(id || '');
  const typedData = data as ExecutionPlanData | undefined;

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Transform execution plan JSON to React Flow nodes and edges
  const transformPlanToGraph = useCallback((planJson: ExecutionPlanNodeData | ExecutionPlanNodeData[]) => {
    const flowNodes: PlanNode[] = [];
    const flowEdges: Edge[] = [];
    const nodeMap = new Map<string, string>();

    const processNode = (node: ExecutionPlanNodeData, parentId?: string, depth = 0): string => {
      const nodeId = node['Node ID'] || node.node_id || `node-${flowNodes.length}`;
      
      // Calculate position based on depth
      const x = depth * 300;
      const y = flowNodes.length * 150;

      const newNode: PlanNode = {
        id: nodeId,
        type: 'custom',
        position: { x, y },
        data: {
          label: node['Node Type'] || node.node_type || 'Unknown',
          nodeType: node['Node Type'] || node.node_type || 'Unknown',
          startupCost: node['Startup Cost'] || node.startup_cost || 0,
          totalCost: node['Total Cost'] || node.total_cost || 0,
          planRows: node['Plan Rows'] || node.plan_rows || 0,
          actualRows: node['Actual Rows'] || node.actual_rows,
          actualLoops: node['Actual Loops'] || node.actual_loops,
          actualTotalTime: node['Actual Total Time'] || node.actual_total_time,
          relationName: node['Relation Name'] || node.relation_name,
          filter: node.Filter,
          sortKey: node['Sort Key'] || node.sort_key,
          joinType: node['Join Type'] || node.join_type,
        },
        style: {
          background: getNodeColor(node['Node Type'] || node.node_type || 'Unknown'),
          border: '2px solid #242830',
          borderRadius: '8px',
          padding: '10px',
          minWidth: '200px',
          color: '#FFFFFF',
        },
      };

      flowNodes.push(newNode);
      nodeMap.set(nodeId, newNode.id);

      // Create edge from parent
      if (parentId) {
        flowEdges.push({
          id: `edge-${parentId}-${nodeId}`,
          source: parentId,
          target: nodeId,
          animated: true,
          style: { stroke: '#3F51B5', strokeWidth: 2 },
        });
      }

      // Process child nodes (Plans)
      if (node.Plans && Array.isArray(node.Plans)) {
        node.Plans.forEach((child: ExecutionPlanNodeData) => {
          processNode(child, nodeId, depth + 1);
        });
      }

      return nodeId;
    };

    // Start processing from the root node
    if (planJson && typeof planJson === 'object') {
      // Handle both array and single node formats
      const rootNode = Array.isArray(planJson) ? planJson[0] : planJson;
      if (rootNode) {
        processNode(rootNode);
      }
    }

    setNodes(flowNodes as unknown as Node[]);
    setEdges(flowEdges);
  }, [setNodes, setEdges]);

  // Transform plan when data changes
  React.useEffect(() => {
    if (data?.planJson) {
      transformPlanToGraph(data.planJson);
    }
  }, [data, transformPlanToGraph]);

  const handleFitView = useCallback(() => {
    // React Flow's fitView functionality
    const bounds = document.querySelector('.react-flow')?.getBoundingClientRect();
    if (bounds) {
      // Simple fit view implementation
      console.log('Fit view called');
    }
  }, []);

  const handleZoomIn = useCallback(() => {
    // Zoom in implementation
    console.log('Zoom in');
  }, []);

  const handleZoomOut = useCallback(() => {
    // Zoom out implementation
    console.log('Zoom out');
  }, []);

  const nodeTypes = useMemo(() => ({
    custom: ({ data }: { data: PlanNode['data'] }) => (
      <Box
        sx={{
          p: 2,
          borderRadius: 2,
          bgcolor: getNodeColor(data.nodeType),
          border: '2px solid #242830',
          minWidth: 200,
        }}
      >
        <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 1 }}>
          {data.label}
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Typography variant="caption" sx={{ color: '#B0B3B8' }}>
            Cost: ${data.totalCost.toFixed(2)}
          </Typography>
          <Typography variant="caption" sx={{ color: '#B0B3B8' }}>
            Rows: {data.planRows}
          </Typography>
          {data.actualRows !== undefined && (
            <Typography variant="caption" sx={{ color: '#10B981' }}>
              Actual: {data.actualRows}
            </Typography>
          )}
          {data.relationName && (
            <Typography variant="caption" sx={{ color: '#3F51B5' }}>
              {data.relationName}
            </Typography>
          )}
        </Box>
      </Box>
    ),
  }), []);

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSkeleton variant="card" count={4} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <ErrorState
          title="Failed to load execution plan"
          message="Unable to fetch execution plan data. Please try again."
          onRetry={() => refetch()}
        />
      </Box>
    );
  }

  if (!data || !data.planJson) {
    return (
      <Box sx={{ p: 3 }}>
        <EmptyState
          variant="no-results"
          title="No execution plan available"
          message="This query does not have an execution plan yet."
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: isMobile ? 2 : 3, bgcolor: '#0F1115', minHeight: '100vh' }}>
      {/* Page Header */}
      <PageHeader
        title="Execution Plan Viewer"
        subtitle="Visualize PostgreSQL EXPLAIN execution plan"
        onRefresh={() => refetch()}
      />

      {/* Summary Cards */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <StatCard
          title="Total Cost"
          value={data.totalCost || 0}
          color="warning"
        />
        <StatCard
          title="Total Rows"
          value={data.totalRows || 0}
          color="info"
        />
        <StatCard
          title="Plan Width"
          value={typedData?.planWidth || 0}
          color="primary"
        />
        <StatCard
          title="Execution Time"
          value={typedData?.executionTimeMs || 0}
          color="success"
        />
      </Box>

      {/* Toolbar */}
      <Paper
        sx={{
          mb: 2,
          p: 1,
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          display: 'flex',
          gap: 1,
          alignItems: 'center',
        }}
      >
        <Tooltip title="Zoom In">
          <IconButton size="small" sx={{ color: '#B0B3B8' }} onClick={handleZoomIn}>
            <ZoomInIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Zoom Out">
          <IconButton size="small" sx={{ color: '#B0B3B8' }} onClick={handleZoomOut}>
            <ZoomOutIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Fit View">
          <IconButton size="small" sx={{ color: '#B0B3B8' }} onClick={handleFitView}>
            <FitScreenIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Box sx={{ flexGrow: 1 }} />
        <Chip label={typedData?.format || 'JSON'} size="small" sx={{ bgcolor: 'rgba(63, 81, 181, 0.1)', color: '#3F51B5' }} />
      </Paper>

      {/* React Flow Graph */}
      <Paper
        sx={{
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          height: '600px',
          position: 'relative',
        }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#242830" />
          <Controls />
        </ReactFlow>
      </Paper>

      {/* Raw JSON View */}
      <Paper
        sx={{
          mt: 3,
          p: 2,
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
        }}
      >
        <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 2 }}>
          Raw Execution Plan JSON
        </Typography>
        <Box
          sx={{
            bgcolor: '#0F1115',
            borderRadius: 1,
            p: 2,
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            color: '#B0B3B8',
            maxHeight: '300px',
            overflow: 'auto',
          }}
        >
          <pre>{JSON.stringify(data.planJson, null, 2)}</pre>
        </Box>
      </Paper>
    </Box>
  );
};

// Helper function to get node color based on node type
function getNodeColor(nodeType: string): string {
  const colorMap: Record<string, string> = {
    'Seq Scan': '#EF4444',
    'Index Scan': '#10B981',
    'Bitmap Heap Scan': '#F59E0B',
    'Bitmap Index Scan': '#3F51B5',
    'Nested Loop': '#EC4899',
    'Hash Join': '#8B5CF6',
    'Merge Join': '#06B6D4',
    'Sort': '#F97316',
    'Aggregate': '#84CC16',
    'Hash': '#14B8A6',
    'Limit': '#6366F1',
    'Result': '#10B981',
  };
  
  return colorMap[nodeType] || '#6B7280';
}
