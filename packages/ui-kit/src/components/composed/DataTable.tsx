/**
 * DataTable component - A comprehensive data table with sorting, filtering, and pagination
 * Built using primitive components with advanced features
 */

import React from 'react';
import { ChevronDown, ChevronUp, MoreHorizontal, Search, Filter, Download } from 'lucide-react';
import { Button } from '../primitives/Button';
import { Input } from '../primitives/Input';
import { Card } from '../primitives/Card';
import { Badge } from '../primitives/Badge';
import { cn } from '../../utils';
import type { DataTableProps, Column } from '../../types';

/**
 * Table Header Cell component
 */
interface TableHeaderCellProps {
  column: Column;
  sortField?: string;
  sortDirection?: 'asc' | 'desc';
  onSort?: (field: string, direction: 'asc' | 'desc') => void;
}

const TableHeaderCell: React.FC<TableHeaderCellProps> = ({
  column,
  sortField,
  sortDirection,
  onSort,
}) => {
  const isSorted = sortField === column.key;
  const nextDirection = isSorted && sortDirection === 'asc' ? 'desc' : 'asc';

  const handleSort = () => {
    if (column.sortable && onSort) {
      onSort(column.key, nextDirection);
    }
  };

  return (
    <th
      className={cn(
        'px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-500',
        column.sortable && 'cursor-pointer hover:text-neutral-700',
        column.align === 'center' && 'text-center',
        column.align === 'right' && 'text-right'
      )}
      onClick={handleSort}
      style={{ width: column.width }}
    >
      <div className="flex items-center gap-1">
        <span>{column.title}</span>
        {column.sortable && (
          <div className="flex flex-col">
            <ChevronUp
              size={12}
              className={cn(
                'transition-colors',
                isSorted && sortDirection === 'asc'
                  ? 'text-primary-600'
                  : 'text-neutral-300'
              )}
            />
            <ChevronDown
              size={12}
              className={cn(
                'transition-colors -mt-1',
                isSorted && sortDirection === 'desc'
                  ? 'text-primary-600'
                  : 'text-neutral-300'
              )}
            />
          </div>
        )}
      </div>
    </th>
  );
};

/**
 * Table Cell component
 */
interface TableCellProps {
  column: Column;
  record: any;
  index: number;
}

const TableCell: React.FC<TableCellProps> = ({ column, record, index }) => {
  const value = column.dataIndex ? record[column.dataIndex] : undefined;
  const content = column.render ? column.render(value, record, index) : value;

  return (
    <td
      className={cn(
        'whitespace-nowrap px-6 py-4 text-sm text-neutral-900',
        column.align === 'center' && 'text-center',
        column.align === 'right' && 'text-right'
      )}
    >
      {content}
    </td>
  );
};

/**
 * Pagination component
 */
interface PaginationProps {
  current: number;
  pageSize: number;
  total: number;
  onChange: (page: number, pageSize: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  current,
  pageSize,
  total,
  onChange,
}) => {
  const totalPages = Math.ceil(total / pageSize);
  const startItem = (current - 1) * pageSize + 1;
  const endItem = Math.min(current * pageSize, total);

  const handlePrevious = () => {
    if (current > 1) {
      onChange(current - 1, pageSize);
    }
  };

  const handleNext = () => {
    if (current < totalPages) {
      onChange(current + 1, pageSize);
    }
  };

  const handlePageSizeChange = (newPageSize: number) => {
    onChange(1, newPageSize);
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxPages = 7; // Maximum number of page buttons to show

    if (totalPages <= maxPages) {
      // Show all pages
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show first page, last page, current page and surrounding pages
      pages.push(1);

      if (current > 3) {
        pages.push('...');
      }

      const start = Math.max(2, current - 1);
      const end = Math.min(totalPages - 1, current + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (current < totalPages - 2) {
        pages.push('...');
      }

      if (totalPages > 1) {
        pages.push(totalPages);
      }
    }

    return pages;
  };

  return (
    <div className="flex items-center justify-between border-t border-neutral-200 bg-white px-4 py-3 sm:px-6">
      <div className="flex flex-1 justify-between sm:hidden">
        <Button
          variant="outline"
          size="sm"
          onClick={handlePrevious}
          disabled={current === 1}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={handleNext}
          disabled={current === totalPages}
        >
          Next
        </Button>
      </div>

      <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <p className="text-sm text-neutral-700">
            Showing <span className="font-medium">{startItem}</span> to{' '}
            <span className="font-medium">{endItem}</span> of{' '}
            <span className="font-medium">{total}</span> results
          </p>

          <select
            value={pageSize}
            onChange={(e) => handlePageSizeChange(Number(e.target.value))}
            className="rounded-md border border-neutral-300 px-2 py-1 text-sm"
          >
            <option value={10}>10 per page</option>
            <option value={25}>25 per page</option>
            <option value={50}>50 per page</option>
            <option value={100}>100 per page</option>
          </select>
        </div>

        <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm">
          <button
            onClick={handlePrevious}
            disabled={current === 1}
            className={cn(
              'relative inline-flex items-center rounded-l-md px-2 py-2 text-sm font-medium',
              'border border-neutral-300 bg-white text-neutral-500 hover:bg-neutral-50',
              'disabled:cursor-not-allowed disabled:opacity-50'
            )}
          >
            Previous
          </button>

          {getPageNumbers().map((page, index) => (
            <React.Fragment key={index}>
              {page === '...' ? (
                <span className="relative inline-flex items-center border border-neutral-300 bg-white px-4 py-2 text-sm font-medium text-neutral-700">
                  ...
                </span>
              ) : (
                <button
                  onClick={() => onChange(page as number, pageSize)}
                  className={cn(
                    'relative inline-flex items-center border px-4 py-2 text-sm font-medium',
                    page === current
                      ? 'z-10 border-primary-500 bg-primary-50 text-primary-600'
                      : 'border-neutral-300 bg-white text-neutral-500 hover:bg-neutral-50'
                  )}
                >
                  {page}
                </button>
              )}
            </React.Fragment>
          ))}

          <button
            onClick={handleNext}
            disabled={current === totalPages}
            className={cn(
              'relative inline-flex items-center rounded-r-md px-2 py-2 text-sm font-medium',
              'border border-neutral-300 bg-white text-neutral-500 hover:bg-neutral-50',
              'disabled:cursor-not-allowed disabled:opacity-50'
            )}
          >
            Next
          </button>
        </nav>
      </div>
    </div>
  );
};

/**
 * Main DataTable component
 */
export const DataTable = <T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  pagination,
  selection,
  sorting,
  filtering,
  emptyState,
  errorState,
  className,
  ...props
}: DataTableProps<T>) => {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedRows, setSelectedRows] = React.useState<string[]>([]);

  // Handle search
  const filteredData = React.useMemo(() => {
    if (!searchQuery) return data;

    return data.filter((record) =>
      columns.some((column) => {
        const value = column.dataIndex ? record[column.dataIndex] : '';
        return String(value).toLowerCase().includes(searchQuery.toLowerCase());
      })
    );
  }, [data, searchQuery, columns]);

  // Handle selection
  const handleSelectAll = () => {
    if (!selection) return;

    const allKeys = data.map(selection.getRowKey);
    const isAllSelected = allKeys.every((key) =>
      selection.selectedKeys.includes(key)
    );

    if (isAllSelected) {
      selection.onChange([]);
    } else {
      selection.onChange(allKeys);
    }
  };

  const handleSelectRow = (record: T) => {
    if (!selection) return;

    const key = selection.getRowKey(record);
    const isSelected = selection.selectedKeys.includes(key);

    if (isSelected) {
      selection.onChange(selection.selectedKeys.filter((k) => k !== key));
    } else {
      selection.onChange([...selection.selectedKeys, key]);
    }
  };

  const isAllSelected = selection && data.length > 0 && 
    data.every((record) => selection.selectedKeys.includes(selection.getRowKey(record)));
  
  const isSomeSelected = selection && selection.selectedKeys.length > 0 && !isAllSelected;

  // Show error state
  if (errorState) {
    return (
      <Card className={cn('p-12 text-center', className)}>
        <div className="mx-auto mb-4 h-12 w-12 text-error-500">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>
        {errorState}
      </Card>
    );
  }

  return (
    <Card className={cn('overflow-hidden', className)} {...props}>
      {/* Table Header */}
      <div className="border-b border-neutral-200 bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Input
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search size={16} />}
              className="w-64"
            />
            
            {filtering && (
              <Button variant="outline" size="sm" leftIcon={<Filter size={16} />}>
                Filters
              </Button>
            )}
          </div>

          <div className="flex items-center gap-2">
            {selection && selection.selectedKeys.length > 0 && (
              <Badge variant="soft" color="primary">
                {selection.selectedKeys.length} selected
              </Badge>
            )}
            
            <Button variant="outline" size="sm" leftIcon={<Download size={16} />}>
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-neutral-200">
          <thead className="bg-neutral-50">
            <tr>
              {selection && (
                <th className="px-6 py-3">
                  <input
                    type="checkbox"
                    checked={isAllSelected}
                    ref={(input) => {
                      if (input) input.indeterminate = !!isSomeSelected;
                    }}
                    onChange={handleSelectAll}
                    className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                </th>
              )}
              
              {columns.map((column) => (
                <TableHeaderCell
                  key={column.key}
                  column={column}
                  sortField={sorting?.field}
                  sortDirection={sorting?.direction}
                  onSort={sorting?.onChange}
                />
              ))}
            </tr>
          </thead>

          <tbody className="divide-y divide-neutral-200 bg-white">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 5 }).map((_, index) => (
                <tr key={index}>
                  {selection && (
                    <td className="px-6 py-4">
                      <div className="h-4 w-4 animate-pulse rounded bg-neutral-200" />
                    </td>
                  )}
                  {columns.map((column) => (
                    <td key={column.key} className="px-6 py-4">
                      <div className="h-4 animate-pulse rounded bg-neutral-200" />
                    </td>
                  ))}
                </tr>
              ))
            ) : filteredData.length === 0 ? (
              // Empty state
              <tr>
                <td
                  colSpan={columns.length + (selection ? 1 : 0)}
                  className="px-6 py-12 text-center"
                >
                  {emptyState || (
                    <div>
                      <p className="text-neutral-500">No data found</p>
                      {searchQuery && (
                        <Button
                          variant="link"
                          size="sm"
                          onClick={() => setSearchQuery('')}
                        >
                          Clear search
                        </Button>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ) : (
              // Data rows
              filteredData.map((record, index) => (
                <tr
                  key={selection ? selection.getRowKey(record) : index}
                  className="hover:bg-neutral-50"
                >
                  {selection && (
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selection.selectedKeys.includes(
                          selection.getRowKey(record)
                        )}
                        onChange={() => handleSelectRow(record)}
                        className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                      />
                    </td>
                  )}
                  
                  {columns.map((column) => (
                    <TableCell
                      key={column.key}
                      column={column}
                      record={record}
                      index={index}
                    />
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && !loading && (
        <Pagination
          current={pagination.current}
          pageSize={pagination.pageSize}
          total={pagination.total}
          onChange={pagination.onChange}
        />
      )}
    </Card>
  );
};

export default DataTable;