-- Migration: Add missing columns to flight_crew and cabin_crew tables
-- Run this before loading mock_flight_data.sql if your tables don't have these columns

-- Add columns to flight_crew table if they don't exist
DO $$ 
BEGIN
    -- Add age column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='flight_crew' AND column_name='age') THEN
        ALTER TABLE flight_crew ADD COLUMN age INTEGER NOT NULL DEFAULT 30;
    END IF;

    -- Add gender column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='flight_crew' AND column_name='gender') THEN
        ALTER TABLE flight_crew ADD COLUMN gender VARCHAR NOT NULL DEFAULT 'Male';
    END IF;

    -- Add nationality column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='flight_crew' AND column_name='nationality') THEN
        ALTER TABLE flight_crew ADD COLUMN nationality VARCHAR NOT NULL DEFAULT 'USA';
    END IF;
END $$;

-- Add columns to cabin_crew table if they don't exist
DO $$ 
BEGIN
    -- Add age column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='cabin_crew' AND column_name='age') THEN
        ALTER TABLE cabin_crew ADD COLUMN age INTEGER NOT NULL DEFAULT 30;
    END IF;

    -- Add gender column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='cabin_crew' AND column_name='gender') THEN
        ALTER TABLE cabin_crew ADD COLUMN gender VARCHAR NOT NULL DEFAULT 'Female';
    END IF;

    -- Add nationality column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='cabin_crew' AND column_name='nationality') THEN
        ALTER TABLE cabin_crew ADD COLUMN nationality VARCHAR NOT NULL DEFAULT 'USA';
    END IF;
END $$;

-- Remove the default values after adding columns (to match the model's NOT NULL without defaults)
DO $$
BEGIN
    -- Flight crew defaults removal
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='flight_crew' AND column_name='age') THEN
        ALTER TABLE flight_crew ALTER COLUMN age DROP DEFAULT;
        ALTER TABLE flight_crew ALTER COLUMN gender DROP DEFAULT;
        ALTER TABLE flight_crew ALTER COLUMN nationality DROP DEFAULT;
    END IF;

    -- Cabin crew defaults removal
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='cabin_crew' AND column_name='age') THEN
        ALTER TABLE cabin_crew ALTER COLUMN age DROP DEFAULT;
        ALTER TABLE cabin_crew ALTER COLUMN gender DROP DEFAULT;
        ALTER TABLE cabin_crew ALTER COLUMN nationality DROP DEFAULT;
    END IF;
END $$;

-- Verify the columns were added
SELECT 'flight_crew columns:' as info;
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'flight_crew' 
AND column_name IN ('age', 'gender', 'nationality')
ORDER BY column_name;

SELECT 'cabin_crew columns:' as info;
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'cabin_crew' 
AND column_name IN ('age', 'gender', 'nationality')
ORDER BY column_name;
