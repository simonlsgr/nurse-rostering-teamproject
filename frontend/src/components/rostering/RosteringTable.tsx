import { InfeasibilityDetails } from "@/types/feasibilityHelperVars";
import { Instance } from "@/types/nurseVars";
import { Tooltip } from "@mui/material";
import { useReactTable, flexRender, getCoreRowModel } from "@tanstack/react-table";

import { getNurseByUid } from "@/lib/roster/dataWrangler";
import React, { useMemo, useState } from "react";
import { getDatesFromTableData, getShiftTypes } from "@/lib/roster/dataWrangler";


export function NurseTableHeader({ table }: { table: ReturnType<typeof useReactTable>; }) {
  return (
    <thead className="bg-gray-200">
      {table.getHeaderGroups().map(hg => (
        <tr key={hg.id} className="position-sticky top-0 ">
          {hg.headers.map(h => (
            <th key={h.id} className="outline px-4 py-2 sticky top-0 first:z-1 first:left-0  bg-gray-200">
              {flexRender(h.column.columnDef.header, h.getContext())}
            </th>
          ))}
        </tr>
      ))}
    </thead>
  );

}


export function NurseTableBody({
  table, setTableData, shift_types, instance, hoveredColumn, setHoveredColumn, infeasibilityDetails
}: {
  table: ReturnType<typeof useReactTable>;
  setTableData: React.Dispatch<React.SetStateAction<any[]>>;
  shift_types: { value: string; label: string; }[];
  instance: Instance;
  hoveredColumn: string | null;
  setHoveredColumn: React.Dispatch<React.SetStateAction<string | null>>;
  infeasibilityDetails: InfeasibilityDetails;
}) {
  return (
    <tbody>
      {table.getRowModel().rows.map(row => (
        <tr key={row.id} className="group box-border">
          {row.getVisibleCells().map(cell => {
            const date = cell.column.id;
            const isNurseColumn = date === "nid";
            const cellValue = String(cell.getValue() ?? "");
            const selectedShift = cellValue === "None" ? "empty" : cellValue;

            const nurseUid = String((row.original as any)?.Nurse ?? "");
            const cellInfeasibility = infeasibilityDetails[Number(nurseUid)]?.[date];
            const cellInfeasibilityNode = (<div>
              {[...(cellInfeasibility ?? new Set<String>())].map((reason, index, arr) => {
                return (
                  <React.Fragment key={reason}>
                    {reason}
                    {index < arr.length - 1 && <br />}
                  </React.Fragment>
                );
              })}
            </div>);



            const hasInfeasibility = cellInfeasibility && cellInfeasibility.size > 0;
            return (
              <Tooltip key={cell.id} title={hasInfeasibility ? cellInfeasibilityNode : ""} placement="top" arrow disableInteractive>
                <td
                  key={cell.id}
                  className={`w-min h-min px-4 py-2 box-border group-hover:border-y-2 hover:bg-gray-400! first:sticky first:outline-1 first:outline-gray-200 left-0 ${hasInfeasibility ? "bg-red-600!" : "bg-white"} ${hoveredColumn == cell.column.id ? "border-x-2" : ""}`}
                  onMouseEnter={() => setHoveredColumn(date)}
                  onMouseLeave={() => setHoveredColumn(null)}
                >
                  {isNurseColumn ? (
                    getNurseByUid(instance, Number(nurseUid))?.name || "Unknown Nurse"
                  ) : (
                    <select
                      name={`shift-${nurseUid}-${date}`}
                      value={selectedShift}
                      onChange={(e) => {
                        const nextShift = e.target.value === "empty" ? "None" : e.target.value;
                        setTableData((prev) => {
                          const updated = prev.map((entry, index) => {
                            if (index !== row.index) return entry;
                            return { ...entry, [date]: nextShift };
                          });
                          return updated;
                        });
                      } }
                      className="p-2 w-full box-border border-2 border-transparent hover:border-blue-500! focus:border-blue-500! focus:outline-none"
                    >
                      {shift_types.map((type) => (
                        <option key={type.value} value={type.value} disabled={getNurseByUid(instance, Number(nurseUid))?.days_off.includes(date) ? true : false}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  )}
                </td>
              </Tooltip>
            );
          })}
        </tr>
      ))}
    </tbody>
  );
}


export function NurseTable({ 
    tableData, setTableData, instance, infeasibilityDetails 
    }: 
    { 
        tableData: any[]; 
        setTableData: React.Dispatch<React.SetStateAction<any[]>>; 
        instance: Instance; 
        infeasibilityDetails: InfeasibilityDetails; }) {

  const dates = getDatesFromTableData(tableData);

  const shift_types = getShiftTypes(instance);

  const [hoveredColumn, setHoveredColumn] = useState<string | null>(null);

  const columns = useMemo(() => [
    {
      header: "Nurse",
      accessorKey: "nid",
    },
    ...dates.map((date) => ({
      header: date,
      accessorKey: date,
    })),
  ],
    [dates]);

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });



  return (
    <div className="overflow-x-auto max-h-[40vh]">
      <table className="border-border border overflow-x-hidden">
        <NurseTableHeader table={table} />
        <NurseTableBody table={table} setTableData={setTableData} shift_types={shift_types} instance={instance} hoveredColumn={hoveredColumn} setHoveredColumn={setHoveredColumn} infeasibilityDetails={infeasibilityDetails} />
      </table>
    </div>
  );
}

