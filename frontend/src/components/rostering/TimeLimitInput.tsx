import { NumberField } from "@base-ui/react";
import { useSolverSettings } from "@/store/solverSettingsStore";


export default function TimeLimitInput() {

    const timeLimit = useSolverSettings((s) => s.timeLimit);
    const setTimeLimit = useSolverSettings((s) => s.setTimeLimit);

    return (
        <div className="p-4">
            <NumberField.Root
                aria-label="Time limit in seconds"
                value={timeLimit}
                min={0}
                max={480}
                step={10}
                onValueChange={(value) => {
                    if (value === null || Number.isNaN(value)) return;
                    setTimeLimit(value);
                }}
                className="w-full"
            >
                <label className="mb-1 block text-sm text-gray-700">Time limit (s)</label>
                <NumberField.Group className="flex items-stretch overflow-hidden rounded-md border border-gray-300 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200">
                    <NumberField.Decrement
                        aria-label="Decrease time limit"
                        className="px-3 text-lg text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        -10
                    </NumberField.Decrement>
                    <NumberField.Input
                        className="w-full border-x border-gray-300 px-3 py-2 outline-none"
                        inputMode="numeric"
                    />
                    <NumberField.Increment
                        aria-label="Increase time limit"
                        className="px-3 text-lg text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        +10
                    </NumberField.Increment>
                </NumberField.Group>
            </NumberField.Root>
        </div>
    );
}
