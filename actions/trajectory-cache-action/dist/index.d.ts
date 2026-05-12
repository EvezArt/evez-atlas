interface RingBuffer<T> {
    buffer: T[];
    size: number;
    head: number;
    tail: number;
    count: number;
}
/**
 * Create a ring buffer for trajectory caching
 */
declare function createRingBuffer<T>(size: number): RingBuffer<T>;
/**
 * Add item to ring buffer
 */
declare function ringBufferPush<T>(rb: RingBuffer<T>, item: T): void;
/**
 * Get items from ring buffer
 */
declare function ringBufferGet<T>(rb: RingBuffer<T>, count: number): T[];
/**
 * Main action entry point
 */
declare function run(): Promise<void>;
export { run, createRingBuffer, ringBufferPush, ringBufferGet };
