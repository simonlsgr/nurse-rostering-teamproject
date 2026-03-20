import { InfeasibilityDetails } from "@/types/feasibilityHelperVars";
import { Instance } from "@/types/nurseVars";
import { Tooltip, Select, MenuItem, NativeSelect } from "@mui/material";
import { useReactTable, flexRender, getCoreRowModel } from "@tanstack/react-table";

import { getNurseByUid } from "@/lib/roster/dataWrangler";
import React, { useMemo, useState } from "react";
import { getDatesFromTableData, getShiftTypes } from "@/lib/roster/dataWrangler";
import { convertShiftTypes, generateDatesFromPlanningHorizon } from "@/lib/utils";
import { useSelectedProject, useShiftTypes } from "@/store/projectStore";


export function NurseTableHeader({ 
  table,
  hoveredColumn,
  setHoveredColumn
}: {
  table: ReturnType<typeof useReactTable>;
  hoveredColumn: string | null;
  setHoveredColumn: React.Dispatch<React.SetStateAction<string | null>>;
}) {
  return (
    <thead className="bg-gray-200">
      {table.getHeaderGroups().map(hg => (
        <tr key={hg.id} className="position-sticky top-0">
          {hg.headers.map(h => (
            <th 
            key={h.id} 
            className={`p-2 sticky top-0 first:z-3 first:left-0 border-1 border-white  bg-gray-200 z-[2] select-none
              ${hoveredColumn == h.column.id ? "not-first:border-x-black" : "border-x-white"}
            `}>
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
    <tbody className="">
      {table.getRowModel().rows.map((row, row_index) => (
        <tr key={row.id} className={`group`}>
          {row.getVisibleCells().map(cell => {
            
            const date = cell.column.id;
            const isNurseColumn = date === "nid";
            const cellValue = String(cell.getValue() ?? "");
            const selectedShift = cellValue === "None" ? "empty" : cellValue;

            const nurseUid = String((row.original as any)?.Nurse ?? "");
            const cellInfeasibility = infeasibilityDetails[Number(nurseUid)]?.[date];
            const isOffDay = getNurseByUid(instance, Number(nurseUid))?.days_off.includes(date);
            const tooltipNode = (<div>
              {isOffDay && <div>A shift cannot be assigned on an "offday".</div>}
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
              <Tooltip key={cell.id} title={hasInfeasibility || isOffDay ? tooltipNode : ""} placement="top" arrow disableInteractive>
                <td
                  key={cell.id}
                  className={`border-1 group-hover:border-y-black border-transparent first:sticky first:z-1 left-0 hover:not-first:bg-gray-400 
                    ${hasInfeasibility ? "bg-red-600!" : row_index % 2 == 0 ? "bg-gray-200" : "bg-white"}
                    
                    ${hoveredColumn == cell.column.id ? "not-first:border-x-black" : row_index % 2 == 0 ? "border-x-white" : "border-x-gray-200"} `}
                  onMouseEnter={() => setHoveredColumn(date)}
                  onMouseLeave={() => setHoveredColumn(null)}
                >
                  {isNurseColumn ? (
                    <p className="text-center cursor-default select-none">{getNurseByUid(instance, Number(nurseUid))?.name || "Unknown Nurse"}</p>
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
                      className="p-4 w-full focus:outline-none z-[0] background-none appearance-none text-center cursor-pointer"
                    >
                      {shift_types.map((type) => (
                        <option className="cursor-pointer" key={type.value} value={type.value} disabled={isOffDay}>
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

  // const dates = getDatesFromTableData(tableData);
  const { selectedProject } = useSelectedProject();
  const { shiftTypes } = useShiftTypes();

  const dates = generateDatesFromPlanningHorizon(selectedProject?.planning_horizon ?? ["", ""]);

  const shift_types = convertShiftTypes(shiftTypes);
  // const shift_types = getShiftTypes(instance);

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
    <div className="overflow-x-auto">
      <table className="border-separate border-spacing-0 overflow-x-hidden">
        <NurseTableHeader table={table} hoveredColumn={hoveredColumn} setHoveredColumn={setHoveredColumn}/>
        <NurseTableBody table={table} setTableData={setTableData} shift_types={shift_types} instance={instance} hoveredColumn={hoveredColumn} setHoveredColumn={setHoveredColumn} infeasibilityDetails={infeasibilityDetails} />
      </table>
    </div>
  );
}

