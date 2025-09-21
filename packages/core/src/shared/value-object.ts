/**
 * Base Value Object class following DDD patterns
 * Value objects are immutable and compared by value equality
 */
export abstract class ValueObject {
  protected abstract getEqualityComponents(): any[];

  public equals(other: ValueObject): boolean {
    if (this === other) return true;
    if (this.constructor !== other.constructor) return false;

    const thisComponents = this.getEqualityComponents();
    const otherComponents = other.getEqualityComponents();

    if (thisComponents.length !== otherComponents.length) return false;

    return thisComponents.every((component, index) => 
      component === otherComponents[index]
    );
  }

  public hashCode(): string {
    return JSON.stringify(this.getEqualityComponents());
  }
}