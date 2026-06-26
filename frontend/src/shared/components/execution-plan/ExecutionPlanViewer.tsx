import React, { useState, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
  NodeTypes,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box,
  Paper,
  Typography,
  useTheme,
  useMediaQuery,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Info,
  Warning,
  Speed,
  Storage,
  MergeType,
  CallSplit,
  Sort,
  Functions,
  FilterList,
} from '@mui/icons-material';

interface ExecutionPlanViewerProps {
  planJson: unknown;
  onNodeSelect?: (node: PlanNode) => void;
}

interface PlanNode {
  id: string;
  type: string;
  cost: number;
  actualRows?: number;
  actualTime?: number;
  planRows?: number;
  planTime?: number;
  relationName?: string;
  indexName?: string;
  alias?: string;
  filter?: string;
  sortKey?: string;
  joinType?: string;
  parentRelationship?: string;
  children?: PlanNode[];
  startupCost?: number;
  totalCost?: number;
  rowsRemovedByFilter?: number;
  rowsRemovedByJoinFilter?: number;
}

interface CustomNodeData {
  type: string;
  cost: number;
  actualRows?: number;
  actualTime?: number;
  planRows?: number;
  planTime?: number;
  relationName?: string;
  indexName?: string;
  alias?: string;
  filter?: string;
  sortKey?: string;
  joinType?: string;
  parentRelationship?: string;
  startupCost?: number;
  totalCost?: number;
  rowsRemovedByFilter?: number;
  rowsRemovedByJoinFilter?: number;
  originalNode: PlanNode;
  isBottleneck: boolean;
}

const CustomNode: React.FC<{ data: CustomNodeData }> = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const getNodeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'seq scan':
        return <FilterList fontSize="small" />;
      case 'index scan':
        return <Storage fontSize="small" />;
      case 'hash join':
      case 'merge join':
        return <MergeType fontSize="small" />;
      case 'nested loop':
        return <CallSplit fontSize="small" />;
      case 'aggregate':
      case 'hash aggregate':
        return <Functions fontSize="small" />;
      case 'sort':
        return <Sort fontSize="small" />;
      default:
        return <Speed fontSize="small" />;
    }
  };

  const getNodeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'seq scan':
        return '#EF4444';
      case 'index scan':
        return '#10B981';
      case 'hash join':
      case 'merge join':
        return '#3F51B5';
      case 'nested loop':
        return '#F59E0B';
      case 'aggregate':
      case 'hash aggregate':
        return '#8B5CF6';
      case 'sort':
        return '#EC4899';
      default:
        return '#6B7280';
    }
  };

  const isBottleneck = data.isBottleneck;
  const nodeColor = getNodeColor(data.type);

  return (
    <Paper
      sx={{
        p: isMobile ? 1 : 1.5,
        minWidth: isMobile ? 150 : 200,
        maxWidth: isMobile ? 180 : 250,
        bgcolor: isBottleneck ? 'rgba(239, 68, 68, 0.1)' : '#1A1D23',
        border: isBottleneck ? '2px solid #EF4444' : `1px solid ${nodeColor}`,
        borderRadius: 2,
        boxShadow: isBottleneck ? '0 0 10px rgba(239, 68, 68, 0.5)' : 'none',
        transition: 'all 0.2s ease',
        '&:hover': {
          bgcolor: '#242830',
          transform: 'scale(1.02)',
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 28,
            height: 28,
            borderRadius: 1,
            bgcolor: `${nodeColor}20`,
            color: nodeColor,
          }}
        >
          {getNodeIcon(data.type)}
        </Box>
        <Typography
          variant="body2"
          sx={{
            color: '#FFFFFF',
            fontWeight: 600,
            fontSize: isMobile ? '0.7rem' : '0.8rem',
            flex: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {data.type}
        </Typography>
        {isBottleneck && (
          <Tooltip title="Performance Bottleneck">
            <Warning fontSize="small" sx={{ color: '#EF4444' }} />
          </Tooltip>
        )}
      </Box>

      {data.relationName && (
        <Typography variant="caption" sx={{ color: '#B0B3B8', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
          {data.relationName}
        </Typography>
      )}

      {data.indexName && (
        <Typography variant="caption" sx={{ color: '#10B981', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
          Index: {data.indexName}
        </Typography>
      )}

      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
        <Chip
          label={`$${data.cost?.toFixed(2)}`}
          size="small"
          sx={{
            bgcolor: 'rgba(245, 158, 11, 0.1)',
            color: '#F59E0B',
            fontSize: '0.65rem',
            height: 18,
          }}
        />
        {data.actualRows !== undefined && (
          <Chip
            label={`${data.actualRows} rows`}
            size="small"
            sx={{
              bgcolor: 'rgba(63, 81, 181, 0.1)',
              color: '#3F51B5',
              fontSize: '0.65rem',
              height: 18,
            }}
          />
        )}
        {data.actualTime !== undefined && (
          <Chip
            label={`${data.actualTime}ms`}
            size="small"
            sx={{
              bgcolor: 'rgba(16, 185, 129, 0.1)',
              color: '#10B981',
              fontSize: '0.65rem',
              height: 18,
            }}
          />
        )}
      </Box>
    </Paper>
  );
};

const nodeTypes: NodeTypes = {
  custom: CustomNode,
};

export const ExecutionPlanViewer: React.FC<ExecutionPlanViewerProps> = ({ planJson, onNodeSelect }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<CustomNodeData | null>(null);
  const [bottlenecks, setBottlenecks] = useState<Set<string>>(new Set());

  const parsePlanNode = useCallback((node: PlanNode, parentId: string | null = null, depth: number = 0): { nodes: Node[]; edges: Edge[] } => {
    const nodeId = node.id || `${node.type}-${depth}-${Math.random().toString(36).substr(2, 9)}`;
    const result: { nodes: Node[]; edges: Edge[] } = { nodes: [], edges: [] };

    const customNode: Node = {
      id: nodeId,
      type: 'custom',
      position: { x: depth * 300, y: 0 },
      data: {
        type: node.type,
        cost: node.cost || node.totalCost || 0,
        actualRows: node.actualRows,
        actualTime: node.actualTime,
        planRows: node.planRows,
        planTime: node.planTime,
        relationName: node.relationName,
        indexName: node.indexName,
        alias: node.alias,
        filter: node.filter,
        sortKey: node.sortKey,
        joinType: node.joinType,
        parentRelationship: node.parentRelationship,
        startupCost: node.startupCost,
        totalCost: node.totalCost,
        rowsRemovedByFilter: node.rowsRemovedByFilter,
        rowsRemovedByJoinFilter: node.rowsRemovedByJoinFilter,
        originalNode: node,
        isBottleneck: false,
      },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    };

    result.nodes.push(customNode);

    if (parentId) {
      result.edges.push({
        id: `${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#3F51B5', strokeWidth: 2 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#3F51B5',
        },
      });
    }

    if (node.children && node.children.length > 0) {
      node.children.forEach((child: PlanNode) => {
        const childResult = parsePlanNode(child, nodeId, depth + 1);
        result.nodes.push(...childResult.nodes);
        result.edges.push(...childResult.edges);
      });
    }

    return result;
  }, []);

  const detectBottlenecks = useCallback((nodes: Node[]) => {
    const costs = nodes.map(n => n.data.cost || 0);
    const maxCost = Math.max(...costs);
    const avgCost = costs.reduce((a, b) => a + b, 0) / costs.length;
    const threshold = avgCost * 2;

    const newBottlenecks = new Set<string>();
    nodes.forEach(node => {
      if ((node.data.cost || 0) > threshold && (node.data.cost || 0) > maxCost * 0.5) {
        newBottlenecks.add(node.id);
        node.data.isBottleneck = true;
      }
    });

    setBottlenecks(newBottlenecks);
  }, []);

  const layoutNodes = useCallback((nodes: Node[], edges: Edge[]) => {
    const nodeMap = new Map<string, Node>();
    nodes.forEach(n => nodeMap.set(n.id, n));

    const levelMap = new Map<string, number>();
    const childrenMap = new Map<string, Node[]>();

    edges.forEach(edge => {
      if (!childrenMap.has(edge.source)) {
        childrenMap.set(edge.source, []);
      }
      childrenMap.get(edge.source)!.push(nodeMap.get(edge.target)!);
    });

    const calculateLevel = (nodeId: string, level: number = 0): number => {
      if (levelMap.has(nodeId)) return levelMap.get(nodeId)!;
      const children = childrenMap.get(nodeId) || [];
      if (children.length === 0) {
        levelMap.set(nodeId, 0);
        return 0;
      }
      const maxChildLevel = Math.max(...children.map(c => calculateLevel(c.id, level + 1)));
      levelMap.set(nodeId, maxChildLevel + 1);
      return maxChildLevel + 1;
    };

    nodes.forEach(node => {
      calculateLevel(node.id);
    });

    const levelGroups = new Map<number, Node[]>();
    nodes.forEach(node => {
      const level = levelMap.get(node.id) || 0;
      if (!levelGroups.has(level)) {
        levelGroups.set(level, []);
      }
      levelGroups.get(level)!.push(node);
    });

    const maxLevel = Math.max(...Array.from(levelGroups.keys()));
    const layoutedNodes = nodes.map(node => {
      const level = levelMap.get(node.id) || 0;
      const levelNodes = levelGroups.get(level) || [];
      const index = levelNodes.indexOf(node);
      const verticalSpacing = 120;
      const horizontalSpacing = 350;
      
      return {
        ...node,
        position: {
          x: (maxLevel - level) * horizontalSpacing,
          y: index * verticalSpacing,
        },
      };
    });

    return layoutedNodes;
  }, []);

  React.useEffect(() => {
    if (planJson) {
      let planData = planJson as PlanNode;
      if ((planJson as Record<string, unknown>).Plan) {
        planData = (planJson as Record<string, unknown>).Plan as PlanNode;
      }

      const { nodes: parsedNodes, edges: parsedEdges } = parsePlanNode(planData);
      const layoutedNodes = layoutNodes(parsedNodes, parsedEdges);
      
      setNodes(layoutedNodes);
      setEdges(parsedEdges);
      detectBottlenecks(layoutedNodes);
    }
  }, [planJson, parsePlanNode, layoutNodes, detectBottlenecks, setNodes, setEdges]);

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.data);
    onNodeSelect?.(node.data.originalNode);
  }, [onNodeSelect]);

  const totalCost = useMemo(() => {
    return nodes.reduce((sum, node) => sum + (node.data.cost || 0), 0);
  }, [nodes]);

  const maxCostNode = useMemo(() => {
    if (nodes.length === 0) return null;
    return nodes.reduce((max, node) => {
      const maxCost = max?.data.cost || 0;
      const nodeCost = node.data.cost || 0;
      return nodeCost > maxCost ? node : max;
    }, nodes[0] as Node | null);
  }, [nodes]);

  const avgCost = useMemo(() => {
    return nodes.length > 0 ? totalCost / nodes.length : 0;
  }, [totalCost, nodes.length]);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: '#0F1115' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, bgcolor: '#1A1D23', borderBottom: '1px solid #242830' }}>
        <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
          Execution Plan
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip label={`${nodes.length} nodes`} size="small" sx={{ bgcolor: 'rgba(63, 81, 181, 0.1)', color: '#3F51B5' }} />
          <Chip label={`${bottlenecks.size} bottlenecks`} size="small" sx={{ bgcolor: 'rgba(239, 68, 68, 0.1)', color: '#EF4444' }} />
        </Box>
      </Box>

      <Box sx={{ flex: 1, position: 'relative' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.2}
          maxZoom={2}
          defaultEdgeOptions={{
            animated: true,
            style: { stroke: '#3F51B5', strokeWidth: 2 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#3F51B5',
            },
          }}
        >
          <Background color="#242830" gap={20} />
          <Controls
            style={{
              backgroundColor: '#1A1D23',
              border: '1px solid #242830',
              borderRadius: 8,
            }}
          />
          <MiniMap
            style={{
              backgroundColor: '#1A1D23',
              border: '1px solid #242830',
            }}
            nodeColor={(node) => {
              if (node.data.isBottleneck) return '#EF4444';
              switch (node.data.type?.toLowerCase()) {
                case 'seq scan': return '#EF4444';
                case 'index scan': return '#10B981';
                case 'hash join':
                case 'merge join': return '#3F51B5';
                case 'nested loop': return '#F59E0B';
                case 'aggregate':
                case 'hash aggregate': return '#8B5CF6';
                case 'sort': return '#EC4899';
                default: return '#6B7280';
              }
            }}
            maskColor="rgba(0, 0, 0, 0.8)"
          />
        </ReactFlow>
      </Box>

      {/* Node Details Panel */}
      {selectedNode && (
        <Paper
          sx={{
            position: 'absolute',
            right: 16,
            top: 16,
            width: isMobile ? 280 : 320,
            maxHeight: '80%',
            overflow: 'auto',
            bgcolor: '#1A1D23',
            border: '1px solid #242830',
            borderRadius: 2,
            zIndex: 10,
          }}
        >
          <Box sx={{ p: 2, borderBottom: '1px solid #242830', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="subtitle1" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
              Node Details
            </Typography>
            <IconButton size="small" onClick={() => setSelectedNode(null)}>
              <Info fontSize="small" sx={{ color: '#B0B3B8' }} />
            </IconButton>
          </Box>
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 600, mb: 1 }}>
              {selectedNode.type}
            </Typography>
            {selectedNode.relationName && (
              <Typography variant="body2" sx={{ color: '#B0B3B8', mb: 2 }}>
                Table: {selectedNode.relationName}
              </Typography>
            )}
            
            <Divider sx={{ my: 2, borderColor: '#242830' }} />
            
            <Grid container spacing={1}>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem' }}>
                  Cost
                </Typography>
                <Typography variant="body2" sx={{ color: '#F59E0B', fontWeight: 600 }}>
                  ${selectedNode.cost?.toFixed(2)}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem' }}>
                  Actual Rows
                </Typography>
                <Typography variant="body2" sx={{ color: '#3F51B5', fontWeight: 600 }}>
                  {selectedNode.actualRows || '-'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem' }}>
                  Actual Time
                </Typography>
                <Typography variant="body2" sx={{ color: '#10B981', fontWeight: 600 }}>
                  {selectedNode.actualTime ? `${selectedNode.actualTime}ms` : '-'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem' }}>
                  Plan Rows
                </Typography>
                <Typography variant="body2" sx={{ color: '#B0B3B8', fontWeight: 600 }}>
                  {selectedNode.planRows || '-'}
                </Typography>
              </Grid>
            </Grid>

            {selectedNode.startupCost !== undefined && selectedNode.totalCost !== undefined && (
              <>
                <Divider sx={{ my: 2, borderColor: '#242830' }} />
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem' }}>
                      Startup Cost
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                      ${selectedNode.startupCost.toFixed(2)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem' }}>
                      Total Cost
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#B0B3B8' }}>
                      ${selectedNode.totalCost.toFixed(2)}
                    </Typography>
                  </Grid>
                </Grid>
              </>
            )}

            {selectedNode.filter && (
              <>
                <Divider sx={{ my: 2, borderColor: '#242830' }} />
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
                  Filter Condition
                </Typography>
                <Typography variant="body2" sx={{ color: '#B0B3B8', fontFamily: 'monospace', fontSize: '0.75rem', wordBreak: 'break-all' }}>
                  {selectedNode.filter}
                </Typography>
              </>
            )}

            {selectedNode.rowsRemovedByFilter !== undefined && (
              <>
                <Divider sx={{ my: 2, borderColor: '#242830' }} />
                <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
                  Rows Removed by Filter
                </Typography>
                <Typography variant="body2" sx={{ color: '#EF4444', fontWeight: 600 }}>
                  {selectedNode.rowsRemovedByFilter}
                </Typography>
              </>
            )}

            {selectedNode.isBottleneck && (
              <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(239, 68, 68, 0.1)', borderRadius: 1, border: '1px solid #EF4444' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Warning fontSize="small" sx={{ color: '#EF4444' }} />
                  <Typography variant="body2" sx={{ color: '#EF4444', fontWeight: 600 }}>
                    Performance Bottleneck
                  </Typography>
                </Box>
                <Typography variant="caption" sx={{ color: '#B0B3B8', fontSize: '0.7rem' }}>
                  This node has significantly higher cost than average. Consider optimization.
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>
      )}

      {/* Cost Analysis Panel */}
      <Paper
        sx={{
          position: 'absolute',
          left: 16,
          bottom: 16,
          width: isMobile ? 200 : 240,
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          zIndex: 10,
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid #242830' }}>
          <Typography variant="subtitle2" sx={{ color: '#FFFFFF', fontWeight: 600 }}>
            Cost Analysis
          </Typography>
        </Box>
        <Box sx={{ p: 2 }}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block' }}>
              Total Cost
            </Typography>
            <Typography variant="h6" sx={{ color: '#F59E0B', fontWeight: 700 }}>
              ${totalCost.toFixed(2)}
            </Typography>
          </Box>
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block' }}>
              Average Cost
            </Typography>
            <Typography variant="body1" sx={{ color: '#B0B3B8', fontWeight: 600 }}>
              ${avgCost.toFixed(2)}
            </Typography>
          </Box>
          {maxCostNode && (
            <Box>
              <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', display: 'block' }}>
                Highest Cost Node
              </Typography>
              <Typography variant="body2" sx={{ color: '#EF4444', fontWeight: 600 }}>
                {maxCostNode.data.type}
              </Typography>
              <Typography variant="caption" sx={{ color: '#B0B3B8', fontSize: '0.7rem' }}>
                ${maxCostNode.data.cost?.toFixed(2)}
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Legend */}
      <Paper
        sx={{
          position: 'absolute',
          left: 16,
          top: 16,
          bgcolor: '#1A1D23',
          border: '1px solid #242830',
          borderRadius: 2,
          p: 1.5,
          zIndex: 10,
        }}
      >
        <Typography variant="caption" sx={{ color: '#FFFFFF', fontWeight: 600, fontSize: '0.7rem', display: 'block', mb: 1 }}>
          Legend
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {[
            { type: 'Seq Scan', color: '#EF4444' },
            { type: 'Index Scan', color: '#10B981' },
            { type: 'Hash Join', color: '#3F51B5' },
            { type: 'Nested Loop', color: '#F59E0B' },
            { type: 'Aggregate', color: '#8B5CF6' },
            { type: 'Sort', color: '#EC4899' },
          ].map((item) => (
            <Box key={item.type} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Box sx={{ width: 12, height: 12, borderRadius: 2, bgcolor: item.color }} />
              <Typography variant="caption" sx={{ color: '#B0B3B8', fontSize: '0.65rem' }}>
                {item.type}
              </Typography>
            </Box>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};
